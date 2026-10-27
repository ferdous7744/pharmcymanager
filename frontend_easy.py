import io
import re
import tkinter as tk
from tkinter import ttk, messagebox
from contextlib import redirect_stdout

import backend as be

FILE = "drug.txt"

# ---------- colors ----------
BG = "#f1f5f9"
HEADER = "#1e3a8a"
BLUE = "#2563eb"
GREEN = "#16a34a"
RED = "#dc2626"
ORANGE = "#f59e0b"
GRAY = "#64748b"
CARD = "#ffffff"
ROW_COLORS = {
    "painkiller": "#fee2e2",   # light red
    "supplement": "#dcfce7",   # light green
    "cold": "#dbeafe",         # light blue
    "other": "#fef9c3",        # light yellow
}
BAD_CHARS = [",", ":", "|"]    # these would break the drug.txt format


def walk(node, out):
    """in-order walk of the tree (left, node, right) - same order as inOrder()"""
    if node is None:
        return
    walk(node.left, out)
    out.append(node)
    walk(node.right, out)


def button(parent, text, color, command):
    return tk.Button(parent, text=text, bg=color, fg="white", activebackground=color,
                     activeforeground="white", relief="flat", bd=0, cursor="hand2",
                     font=("Segoe UI", 10, "bold"), padx=10, pady=6, command=command)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drug Administration")
        self.geometry("1180x680")
        self.minsize(1000, 600)
        self.configure(bg=BG)

        self.root_node = be.BuildTree(FILE)
        self.selected = None      # the drug node currently selected in the table
        self.draft = []           # products of a NEW drug (before adding it)
        self.node_of = {}         # table row id -> node

        self.build_style()
        self.build_header()
        self.build_toolbar()
        self.build_body()
        self.build_status()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()
        self.status("Welcome! Click a drug in the table to see or edit it.", "info")

    # ================= UI =================
    def build_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", rowheight=30, font=("Segoe UI", 10), borderwidth=0)
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background=BLUE, foreground="white", relief="flat")
        s.map("Treeview.Heading", background=[("active", HEADER)])
        s.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", "white")])
        s.configure("TCombobox", padding=4)

    def build_header(self):
        h = tk.Frame(self, bg=HEADER)
        h.pack(fill="x")
        tk.Label(h, text="💊  Drug Administration", bg=HEADER, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=16, pady=12)
        button(h, "💾  Save & Exit", GREEN, self.save_exit).pack(side="right", padx=16, pady=10)

    def build_toolbar(self):
        t = tk.Frame(self, bg=BG)
        t.pack(fill="x", padx=14, pady=(12, 4))

        tk.Label(t, text="Find by ID:", bg=BG, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(t, textvariable=self.search_var, width=8).pack(side="left", padx=4)
        button(t, "🔍 Find", BLUE, self.search_id).pack(side="left", padx=(0, 18))

        tk.Label(t, text="Drugs containing product:", bg=BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        self.filter_var = tk.StringVar()
        ttk.Entry(t, textvariable=self.filter_var, width=12).pack(side="left", padx=4)
        button(t, "Filter", BLUE, self.filter_product).pack(side="left", padx=2)
        button(t, "Show all", GRAY, lambda: self.refresh()).pack(side="left", padx=2)

        self.count_label = tk.Label(t, text="", bg=BG, fg=GRAY, font=("Segoe UI", 10))
        self.count_label.pack(side="right")

    def build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=8)

        # ---------- table (left) ----------
        left = tk.Frame(body, bg=CARD)
        left.pack(side="left", fill="both", expand=True)
        cols = ("id", "name", "price", "category", "products")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, w in zip(cols, (50, 130, 80, 110, 260)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="w" if c in ("name", "category", "products") else "center")
        for tag, color in ROW_COLORS.items():
            self.tree.tag_configure(tag, background=color)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ---------- form (right) ----------
        right = tk.Frame(body, bg=CARD, padx=14, pady=12)
        right.pack(side="right", fill="y", padx=(12, 0))

        self.form_title = tk.Label(right, text="➕ New drug", bg=CARD, fg=HEADER,
                                   font=("Segoe UI", 14, "bold"))
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.v_id, self.v_name = tk.StringVar(), tk.StringVar()
        self.v_price, self.v_cat = tk.StringVar(), tk.StringVar()

        def field(row, label, widget):
            tk.Label(right, text=label, bg=CARD, font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=3)
            widget.grid(row=row, column=1, sticky="ew", pady=3, padx=(8, 0))

        self.e_id = ttk.Entry(right, textvariable=self.v_id, width=24)
        field(1, "ID", self.e_id)
        field(2, "Name", ttk.Entry(right, textvariable=self.v_name, width=24))
        field(3, "Price", ttk.Entry(right, textvariable=self.v_price, width=24))
        self.cat_box = ttk.Combobox(right, textvariable=self.v_cat, width=22)
        field(4, "Category", self.cat_box)

        # products
        tk.Label(right, text="Products", bg=CARD, fg=HEADER,
                 font=("Segoe UI", 11, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(12, 2))
        self.plist = tk.Listbox(right, height=5, font=("Segoe UI", 10), activestyle="none",
                                selectbackground=BLUE, exportselection=False)
        self.plist.grid(row=6, column=0, columnspan=2, sticky="ew")

        pf = tk.Frame(right, bg=CARD)
        pf.grid(row=7, column=0, columnspan=2, sticky="ew", pady=4)
        self.v_pname, self.v_pamount = tk.StringVar(), tk.StringVar()
        tk.Label(pf, text="Name", bg=CARD).pack(side="left")
        ttk.Entry(pf, textvariable=self.v_pname, width=9).pack(side="left", padx=3)
        tk.Label(pf, text="Amount", bg=CARD).pack(side="left")
        ttk.Entry(pf, textvariable=self.v_pamount, width=6).pack(side="left", padx=3)
        button(pf, "+", GREEN, self.add_product).pack(side="left", padx=3)
        button(right, "Remove selected product", ORANGE, self.remove_product).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=2)

        # main buttons
        button(right, "➕  Add as new drug", GREEN, self.add_drug).grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(14, 3))
        button(right, "💾  Save changes", BLUE, self.save_changes).grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=3)
        button(right, "🗑  Delete this drug", RED, self.delete_drug).grid(
            row=11, column=0, columnspan=2, sticky="ew", pady=3)
        button(right, "🧹  Clear / New drug", GRAY, self.clear_form).grid(
            row=12, column=0, columnspan=2, sticky="ew", pady=3)

        # replace product everywhere
        tk.Label(right, text="Rename a product in ALL drugs", bg=CARD, fg=HEADER,
                 font=("Segoe UI", 11, "bold")).grid(row=13, column=0, columnspan=2, sticky="w", pady=(14, 2))
        rf = tk.Frame(right, bg=CARD)
        rf.grid(row=14, column=0, columnspan=2, sticky="ew")
        self.v_old, self.v_new = tk.StringVar(), tk.StringVar()
        ttk.Entry(rf, textvariable=self.v_old, width=9).pack(side="left")
        tk.Label(rf, text=" ➜ ", bg=CARD).pack(side="left")
        ttk.Entry(rf, textvariable=self.v_new, width=9).pack(side="left")
        button(rf, "Rename", BLUE, self.replace_product).pack(side="left", padx=6)

    def build_status(self):
        self.status_label = tk.Label(self, text="", anchor="w", font=("Segoe UI", 10, "bold"),
                                     padx=14, pady=6)
        self.status_label.pack(fill="x", side="bottom")

    # ================= helpers =================
    def status(self, msg, kind="info"):
        colors = {"ok": ("#dcfce7", "#166534"), "error": ("#fee2e2", "#991b1b"),
                  "info": ("#e0e7ff", "#1e3a8a")}
        bg, fg = colors[kind]
        self.status_label.configure(text=msg, bg=bg, fg=fg)

    def run(self, fn, *args):
        """call a backend function and capture what it prints. returns (result, ok, printed text)"""
        buf = io.StringIO()
        result, ok = None, True
        try:
            with redirect_stdout(buf):
                result = fn(*args)
        except Exception as e:
            ok = False
            buf.write(f"{e}")
        return result, ok, buf.getvalue()

    def refresh(self, only_ids=None):
        nodes = []
        walk(self.root_node, nodes)
        self.tree.delete(*self.tree.get_children())
        self.node_of = {}
        cats = set()
        shown = 0
        for n in nodes:
            cat = str(n.category).strip()
            cats.add(cat)
            if only_ids is not None and n.id not in only_ids:
                continue
            tag = cat.lower() if cat.lower() in ROW_COLORS else "other"
            iid = self.tree.insert("", "end", tags=(tag,), values=(
                n.id, str(n.name).strip(), n.price, cat, be.listToText(n.product)))
            self.node_of[iid] = n
            shown += 1
        self.cat_box["values"] = sorted(c for c in cats if c)
        self.count_label.configure(text=f"{shown} drug(s)")
        # keep the same drug selected
        if self.selected is not None:
            for iid, n in self.node_of.items():
                if n is self.selected:
                    self.tree.selection_set(iid)
                    break

    def products_of(self, node):
        items = []
        cur = node.product
        while cur is not None:
            items.append((cur.name, cur.amount))
            cur = cur.next
        return items

    def refresh_products(self):
        self.plist.delete(0, "end")
        items = self.products_of(self.selected) if self.selected is not None else self.draft
        for name, amount in items:
            self.plist.insert("end", f"{str(name).strip()}  :  {amount}")

    def set_id_locked(self, locked):
        self.e_id.configure(state="readonly" if locked else "normal")

    # ================= events =================
    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        node = self.node_of[sel[0]]
        self.selected = node
        self.set_id_locked(False)
        self.v_id.set(node.id)
        self.set_id_locked(True)           # the ID is the tree key, so it can't be edited
        self.v_name.set(str(node.name).strip())
        self.v_price.set(node.price)
        self.v_cat.set(str(node.category).strip())
        self.form_title.configure(text=f"✏️ Edit drug #{node.id}")
        self.refresh_products()

    def clear_form(self):
        self.selected = None
        self.draft = []
        self.tree.selection_remove(self.tree.selection())
        self.set_id_locked(False)
        for v in (self.v_id, self.v_name, self.v_price, self.v_cat, self.v_pname, self.v_pamount):
            v.set("")
        self.form_title.configure(text="➕ New drug")
        self.refresh_products()
        self.status("Form cleared. Fill it in to add a new drug.", "info")

    # ================= validation =================
    def read_basic(self):
        name = self.v_name.get().strip()
        cat = self.v_cat.get().strip()
        if not name or not cat:
            self.status("Please fill in the name and the category.", "error")
            return None
        try:
            price = float(self.v_price.get())
        except ValueError:
            self.status("Price must be a number.", "error")
            return None
        for ch in BAD_CHARS:
            if ch in name or ch in cat:
                self.status(f"Name and category can't contain  ,  :  |   (found '{ch}')", "error")
                return None
        return name, price, cat

    # ================= actions =================
    def add_product(self):
        name = self.v_pname.get().strip()
        if not name or any(ch in name for ch in BAD_CHARS):
            self.status("Product name is empty or contains , : |", "error")
            return
        try:
            amount = int(self.v_pamount.get())
        except ValueError:
            self.status("Product amount must be a whole number.", "error")
            return
        if self.selected is not None:
            new = be.ListNode(name, amount)
            if self.selected.product is None:
                self.selected.product = new
            else:
                cur = self.selected.product
                while cur.next is not None:
                    cur = cur.next
                cur.next = new
            self.refresh()
        else:
            self.draft.append((name, amount))
        self.v_pname.set("")
        self.v_pamount.set("")
        self.refresh_products()
        self.status(f"Product '{name}' added.", "ok")

    def remove_product(self):
        pick = self.plist.curselection()
        if not pick:
            self.status("Click a product in the list first.", "error")
            return
        index = pick[0]
        if self.selected is not None:
            name = self.products_of(self.selected)[index][0]
            _, ok, _ = self.run(be.deletProduct, self.root_node, self.selected.id, name)
            self.refresh()
        else:
            self.draft.pop(index)
        self.refresh_products()
        self.status("Product removed.", "ok")

    def add_drug(self):
        if self.selected is not None:
            self.status("A drug is selected. Press 'Clear / New drug' first.", "error")
            return
        try:
            id_ = int(self.v_id.get())
        except ValueError:
            self.status("ID must be a whole number.", "error")
            return
        basic = self.read_basic()
        if basic is None:
            return
        name, price, cat = basic
        text = "|".join(f"{n}:{a}" for n, a in self.draft) or "NULL"
        new_root, ok, msg = self.run(be.addDrug, self.root_node, id_, name, price, cat, text)
        if not ok:
            self.status(f"Error: {msg}", "error")
            return
        self.root_node = new_root
        self.clear_form()
        self.refresh()
        self.status(f"Drug '{name}' added successfully!", "ok")

    def save_changes(self):
        if self.selected is None:
            self.status("Click a drug in the table first.", "error")
            return
        basic = self.read_basic()
        if basic is None:
            return
        name, price, cat = basic
        id_ = self.selected.id
        for field, value in (("name", name), ("price", price), ("category", cat)):
            _, ok, msg = self.run(be.modifyDrug, self.root_node, id_, field, str(value))
            if not ok:
                self.status(f"Error: {msg}", "error")
                return
        self.refresh()
        self.status(f"Drug #{id_} updated.", "ok")

    def delete_drug(self):
        if self.selected is None:
            self.status("Click a drug in the table first.", "error")
            return
        id_, name = self.selected.id, str(self.selected.name).strip()
        if not messagebox.askyesno("Delete", f"Delete '{name}' (ID {id_})?"):
            return
        new_root, ok, msg = self.run(be.deleteNode, self.root_node, id_)
        if not ok:
            self.status(f"Error: {msg}", "error")
            return
        self.root_node = new_root
        self.selected = None
        self.clear_form()
        self.refresh()
        self.status(f"Drug '{name}' deleted.", "ok")

    def search_id(self):
        try:
            id_ = int(self.search_var.get())
        except ValueError:
            self.status("ID must be a whole number.", "error")
            return
        found, ok, _ = self.run(be.search, id_, self.root_node)
        if not (ok and found):
            self.status(f"No drug with ID {id_}.", "error")
            return
        self.refresh()
        for iid, n in self.node_of.items():
            if n.id == id_:
                self.tree.selection_set(iid)
                self.tree.see(iid)
                break
        self.status(f"Found drug #{id_}.", "ok")

    def filter_product(self):
        name = self.filter_var.get().strip()
        if not name:
            self.status("Type a product name first (example: Para).", "error")
            return
        _, _, printed = self.run(be.displayPro, self.root_node, name)
        ids = {int(i) for i in re.findall(r"drug id : (\d+)", printed)}
        self.refresh(only_ids=ids)
        if ids:
            self.status(f"{len(ids)} drug(s) contain '{name}'.", "ok")
        else:
            self.status(f"No drug contains '{name}'.", "error")

    def replace_product(self):
        old, new = self.v_old.get().strip(), self.v_new.get().strip()
        if not old or not new or any(ch in new for ch in BAD_CHARS):
            self.status("Fill in both names (without , : |).", "error")
            return
        _, ok, printed = self.run(be.replace, self.root_node, old, new)
        count = printed.count("Done !")
        self.refresh()
        self.refresh_products()
        if count:
            self.status(f"'{old}' renamed to '{new}' in {count} drug(s).", "ok")
        else:
            self.status(f"No drug contains '{old}'.", "error")

    # ================= exit =================
    def save_exit(self):
        be.saveTree(self.root_node, FILE)
        self.destroy()

    def on_close(self):
        answer = messagebox.askyesnocancel("Exit", "Save before closing?")
        if answer is None:
            return
        if answer:
            be.saveTree(self.root_node, FILE)
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
