import tkinter as tk
from tkinter import messagebox
import math

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0

class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left:
                self._insert_recursive(node.left, value)
            else:
                node.left = Node(value)
        elif value > node.value:
            if node.right:
                self._insert_recursive(node.right, value)
            else:
                node.right = Node(value)
        # Duplicate values are ignored

    def delete(self, value):
        self.root = self._delete_recursive(self.root, value)

    def _delete_recursive(self, node, value):
        if not node:
            return None

        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            temp = self._min_value_node(node.right)
            node.value = temp.value
            node.right = self._delete_recursive(node.right, temp.value)
        return node

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def search(self, value):
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        if not node or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

    def clear(self):
        self.root = None

    def get_inorder(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.value)
            self._inorder_recursive(node.right, result)

class BSTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("BST Visualizer")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1E1E1E")

        self.bst = BST()
        self.node_radius = 20
        self.vertical_spacing = 60
        self.highlighted_node = None

        self._setup_ui()

    def _setup_ui(self):
        # Control Panel
        control_frame = tk.Frame(self.root, bg="#252526", pady=10)
        control_frame.pack(fill=tk.X)

        label_font = ("Consolas", 10)
        button_font = ("Consolas", 10, "bold")

        tk.Label(control_frame, text="Value:", bg="#252526", fg="#CCCCCC", font=label_font).pack(side=tk.LEFT, padx=(20, 5))
        
        self.value_entry = tk.Entry(control_frame, bg="#3C3C3C", fg="white", insertbackground="white", borderwidth=0, font=label_font, width=10)
        self.value_entry.pack(side=tk.LEFT, padx=5)
        self.value_entry.bind("<Return>", lambda e: self.insert_node())

        # Buttons
        self._create_button(control_frame, "Insert", self.insert_node, "#007ACC")
        self._create_button(control_frame, "Delete", self.delete_node, "#CC3333")
        self._create_button(control_frame, "Search", self.search_node, "#D18616")
        self._create_button(control_frame, "Bulk", self.bulk_insert, "#6A9955")
        self._create_button(control_frame, "Clear", self.clear_tree, "#808080")

        # Canvas
        self.canvas = tk.Canvas(self.root, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status & Info Bar
        info_frame = tk.Frame(self.root, bg="#007ACC", height=25)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(info_frame, text="Ready", bg="#007ACC", fg="white", font=("Consolas", 9))
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.inorder_label = tk.Label(info_frame, text="In-order: []", bg="#007ACC", fg="white", font=("Consolas", 9))
        self.inorder_label.pack(side=tk.RIGHT, padx=10)

        # Handle window resizing
        self.root.bind("<Configure>", lambda e: self.update_view())

    def _create_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white", 
                        activebackground=color, activeforeground="white",
                        relief=tk.FLAT, font=("Consolas", 10, "bold"), padx=10)
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def insert_node(self):
        val_str = self.value_entry.get().strip()
        if not val_str: return
        try:
            val = int(val_str)
            self.bst.insert(val)
            self.value_entry.delete(0, tk.END)
            self.update_view(f"Inserted {val}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def delete_node(self):
        val_str = self.value_entry.get().strip()
        if not val_str: return
        try:
            val = int(val_str)
            self.bst.delete(val)
            self.value_entry.delete(0, tk.END)
            self.update_view(f"Deleted {val}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def search_node(self):
        val_str = self.value_entry.get().strip()
        if not val_str: return
        try:
            val = int(val_str)
            node = self.bst.search(val)
            if node:
                self.highlighted_node = node
                self.update_view(f"Found {val}")
            else:
                self.highlighted_node = None
                self.update_view(f"Value {val} not found")
                messagebox.showinfo("Search", f"Value {val} not found in the tree.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def bulk_insert(self):
        val_str = self.value_entry.get().strip()
        if not val_str: return
        try:
            values = [int(v.strip()) for v in val_str.replace(",", " ").split() if v.strip()]
            for v in values:
                self.bst.insert(v)
            self.value_entry.delete(0, tk.END)
            self.update_view(f"Bulk inserted {len(values)} values")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers separated by commas or spaces.")

    def clear_tree(self):
        self.bst.clear()
        self.highlighted_node = None
        self.update_view("Tree cleared")

    def update_view(self, message="Ready"):
        self.canvas.delete("all")
        if self.bst.root:
            self._draw_tree(self.bst.root, 0, self.canvas.winfo_width(), 40, self.canvas.winfo_width() // 2)
        
        self.status_label.config(text=message)
        inorder = self.bst.get_inorder()
        self.inorder_label.config(text=f"In-order: {inorder}")

    def _draw_tree(self, node, x_min, x_max, y, parent_x=None, parent_y=None):
        if not node:
            return

        x = (x_min + x_max) // 2
        node.x = x
        node.y = y

        # Draw edge to parent
        if parent_x is not None and parent_y is not None:
            self.canvas.create_line(parent_x, parent_y, x, y, fill="#444444", width=1)

        # Draw child subtrees
        self._draw_tree(node.left, x_min, x, y + self.vertical_spacing, x, y)
        self._draw_tree(node.right, x, x_max, y + self.vertical_spacing, x, y)

        # Draw node
        color = "#007ACC"
        if self.highlighted_node and self.highlighted_node.value == node.value:
            color = "#D18616"
        
        # Circle
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius,
                                fill=color, outline="#FFFFFF", width=1)
        
        # Text
        self.canvas.create_text(x, y, text=str(node.value), fill="white", font=("Consolas", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = BSTVisualizer(root)
    
    # Wait for window to render before drawing for correct canvas width
    root.update()
    app.update_view()
    
    root.mainloop()
