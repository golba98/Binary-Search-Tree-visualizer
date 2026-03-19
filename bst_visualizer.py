import sys
import math
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QSlider, QGraphicsView, QGraphicsScene, QMessageBox)
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt6.QtCore import Qt, QTimer

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.x = 0.0
        self.y = 0.0
        self.prelim = 0.0
        self.mod = 0.0
        self.ancestor = self
        self.thread = None
        self.change = 0.0
        self.shift = 0.0
        self.depth = 0


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            self._insert_rec(self.root, value)

    def _insert_rec(self, node, value):
        if value < node.value:
            if node.left:
                self._insert_rec(node.left, value)
            else:
                node.left = Node(value)
        elif value > node.value:
            if node.right:
                self._insert_rec(node.right, value)
            else:
                node.right = Node(value)

    def delete(self, value):
        self.root = self._delete_rec(self.root, value)

    def _delete_rec(self, node, value):
        if not node:
            return None
        if value < node.value:
            node.left = self._delete_rec(node.left, value)
        elif value > node.value:
            node.right = self._delete_rec(node.right, value)
        else:
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            successor = self._min_node(node.right)
            node.value = successor.value
            node.right = self._delete_rec(node.right, successor.value)
        return node

    def _min_node(self, node):
        while node.left:
            node = node.left
        return node

    def search(self, value):
        return self._search_rec(self.root, value)

    def _search_rec(self, node, value):
        if not node or node.value == value:
            return node
        if value < node.value:
            return self._search_rec(node.left, value)
        return self._search_rec(node.right, value)

    def search_with_path(self, value):
        path = []
        node = self.root
        while node:
            path.append(node)
            if value == node.value:
                return path, node
            elif value < node.value:
                node = node.left
            else:
                node = node.right
        return path, None

    def clear(self):
        self.root = None

    def get_inorder(self):
        result = []
        self._inorder_rec(self.root, result)
        return result

    def _inorder_rec(self, node, result):
        if node:
            self._inorder_rec(node.left, result)
            result.append(node.value)
            self._inorder_rec(node.right, result)

    def get_inorder_nodes(self):
        result = []
        self._inorder_nodes_rec(self.root, result)
        return result

    def _inorder_nodes_rec(self, node, result):
        if node:
            self._inorder_nodes_rec(node.left, result)
            result.append(node)
            self._inorder_nodes_rec(node.right, result)

    def get_preorder_nodes(self):
        result = []
        self._preorder_rec(self.root, result)
        return result

    def _preorder_rec(self, node, result):
        if node:
            result.append(node)
            self._preorder_rec(node.left, result)
            self._preorder_rec(node.right, result)

    def get_postorder_nodes(self):
        result = []
        self._postorder_rec(self.root, result)
        return result

    def _postorder_rec(self, node, result):
        if node:
            self._postorder_rec(node.left, result)
            self._postorder_rec(node.right, result)
            result.append(node)

    def get_height(self):
        return self._height_rec(self.root)

    def _height_rec(self, node):
        if not node:
            return 0
        return 1 + max(self._height_rec(node.left), self._height_rec(node.right))

    def is_balanced(self):
        return self._check_balanced(self.root) != -1

    def _check_balanced(self, node):
        if not node:
            return 0
        lh = self._check_balanced(node.left)
        if lh == -1:
            return -1
        rh = self._check_balanced(node.right)
        if rh == -1:
            return -1
        if abs(lh - rh) > 1:
            return -1
        return 1 + max(lh, rh)

    def find_inorder_successor(self, value):
        node = self.search(value)
        if not node:
            return None
        if node.right:
            return self._min_node(node.right)
        successor = None
        current = self.root
        while current:
            if value < current.value:
                successor = current
                current = current.left
            elif value > current.value:
                current = current.right
            else:
                break
        return successor


MARGIN = 60
H_SPACING = 60
V_SPACING = 80


class LayoutEngine:
    def compute(self, root, h_spacing=H_SPACING, v_spacing=V_SPACING):
        if not root:
            return
        self._hs = h_spacing
        self._vs = v_spacing
        self._counter = [0]
        self._assign(root, 0)

    def _assign(self, node, depth):
        if not node:
            return
        self._assign(node.left, depth + 1)
        node.x = MARGIN + self._counter[0] * self._hs
        node.y = MARGIN + depth * self._vs
        node.depth = depth
        self._counter[0] += 1
        self._assign(node.right, depth + 1)


class AnimationQueue:
    def __init__(self, parent=None):
        self._q = deque()
        self._running = False
        self._timer = QTimer(parent)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._next_step)
        self._current_seq = None

    def enqueue(self, seq):
        self._q.append(list(seq))
        if not self._running:
            self._next()

    def clear(self):
        self._q.clear()
        self._timer.stop()
        self._running = False
        self._current_seq = None

    def _next(self):
        if not self._q:
            self._running = False
            return
        self._running = True
        self._current_seq = self._q.popleft()
        self._next_step()

    def _next_step(self):
        if not self._current_seq:
            self._next()
            return
        delay, cb = self._current_seq.pop(0)
        try:
            cb()
        except Exception:
            pass
        
        if self._current_seq:
            if delay > 0:
                self._timer.start(delay)
            else:
                QTimer.singleShot(0, self._next_step)
        else:
            self._next()


NODE_R = 20

# Black and White Theme Colors
CF_ROOT  = '#000000'
CO_ROOT  = '#FFFFFF'
CF_INT   = '#222222'
CO_INT   = '#CCCCCC'
CF_LEAF  = '#444444'
CO_LEAF  = '#AAAAAA'
CF_INS   = '#FFFFFF'
CO_INS   = '#000000'
CF_DEL   = '#555555'
CO_DEL   = '#FFFFFF'
CF_FOUND = '#FFFFFF'
CO_FOUND = '#000000'
CF_PATH  = '#333333'
CF_TCUR  = '#FFFFFF'
CO_TCUR  = '#000000'
CF_TVIS  = '#666666'
CO_TVIS  = '#FFFFFF'


class BSTGraphicsView(QGraphicsView):
    def __init__(self, bst, layout, parent=None):
        super().__init__(parent)
        self.bst = bst
        self.layout_engine = layout
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor('#1E1E1E')))
        self.setStyleSheet("border: none;")

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

    def reset_view(self):
        self.resetTransform()
        self.centerOn(0, 0)
        self.full_redraw()

    def full_redraw(self, hmap=None, rmap=None):
        self.scene.clear()
        hmap = hmap or {}
        rmap = rmap or {}
        self.layout_engine.compute(self.bst.root)
        if not self.bst.root:
            return
        
        self._draw_edges(self.bst.root)
        self._draw_nodes(self.bst.root, hmap, rmap)
        
        # Adjust scene rect with padding to allow panning
        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect.adjusted(-200, -200, 200, 200))

    def _draw_edges(self, n):
        if not n:
            return
        for c in (n.left, n.right):
            if c:
                pen = QPen(QColor('#555555'))
                pen.setWidth(2)
                self.scene.addLine(n.x, n.y, c.x, c.y, pen)
                self._draw_edges(c)

    def _draw_nodes(self, n, hmap, rmap):
        if not n:
            return
        self._draw_nodes(n.left, hmap, rmap)
        self._draw_nodes(n.right, hmap, rmap)
        
        r = rmap.get(n.value, NODE_R)
        if r < 1:
            return
        
        if n.value in hmap:
            fill_hex, out_hex, ow = hmap[n.value]
        elif n is self.bst.root:
            fill_hex, out_hex, ow = CF_ROOT, CO_ROOT, 2
        elif not n.left and not n.right:
            fill_hex, out_hex, ow = CF_LEAF, CO_LEAF, 1
        else:
            fill_hex, out_hex, ow = CF_INT, CO_INT, 1
            
        pen = QPen(QColor(out_hex))
        pen.setWidth(ow)
        brush = QBrush(QColor(fill_hex))
        
        ellipse = self.scene.addEllipse(n.x - r, n.y - r, r*2, r*2, pen, brush)
        
        lv = n.left.value if n.left else 'None'
        rv = n.right.value if n.right else 'None'
        ellipse.setToolTip(f"Value: {n.value}\nDepth: {n.depth}\nLeft: {lv}\nRight: {rv}")
        
        if r >= 8:
            text = self.scene.addText(str(n.value), QFont('Consolas', 11, QFont.Weight.Bold))
            text.setDefaultTextColor(QColor('white'))
            br = text.boundingRect()
            text.setPos(n.x - br.width()/2, n.y - br.height()/2)
            
            # Forward hover events to the ellipse so tooltip works cleanly when hovering over text
            text.setToolTip(ellipse.toolTip())
            
        if n is self.bst.root:
            root_text = self.scene.addText('R', QFont('Consolas', 8, QFont.Weight.Bold))
            root_text.setDefaultTextColor(QColor(CO_ROOT))
            br = root_text.boundingRect()
            root_text.setPos(n.x - br.width()/2, n.y - r - 20)


class BSTVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BST Visualizer')
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #000000; }
            QWidget { 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; 
                font-size: 14px;
                color: #FFFFFF; 
            }
            #HeaderPanel {
                background-color: #111111;
                border-bottom: 1px solid #333333;
            }
            QLineEdit { 
                background-color: #000000; 
                border: 1px solid #555555; 
                padding: 6px 12px; 
                color: #FFFFFF; 
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #FFFFFF;
            }
            QPushButton { 
                border: 1px solid #333333; 
                padding: 8px 16px; 
                font-weight: 600; 
                border-radius: 6px; 
                color: #FFFFFF;
                background-color: #222222;
            }
            QPushButton:hover { 
                background-color: #444444; 
                border: 1px solid #666666;
            }
            QPushButton[btnClass="primary"] { background-color: #FFFFFF; color: #000000; border: 1px solid #FFFFFF; }
            QPushButton[btnClass="primary"]:hover { background-color: #CCCCCC; }
            
            QSlider::groove:horizontal { 
                border: 1px solid #333333; 
                height: 6px; 
                background: #111111; 
                border-radius: 3px; 
            }
            QSlider::handle:horizontal { 
                background: #FFFFFF; 
                width: 16px; 
                height: 16px;
                margin: -5px 0; 
                border-radius: 8px; 
            }
            QSlider::handle:horizontal:hover {
                background: #CCCCCC;
            }
            QLabel { color: #FFFFFF; }
            #StatusBar { 
                background-color: #111111; 
                border-top: 1px solid #333333;
            }
            #StatsBar { 
                background-color: #000000; 
                border-top: 1px solid #111111;
            }
        """)
        
        self.bst = BST()
        self.layout_engine = LayoutEngine()
        self._setup_ui()
        self.anim = AnimationQueue(self)
        self._redraw()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Combined Header Panel
        header = QWidget()
        header.setObjectName("HeaderPanel")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(12)

        # Row 1: Operations
        r1_layout = QHBoxLayout()
        r1_layout.setSpacing(10)
        
        title_label = QLabel("BST Visualizer")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; margin-right: 20px;")
        r1_layout.addWidget(title_label)

        r1_layout.addWidget(QLabel("Value:"))
        self.entry = QLineEdit()
        self.entry.setFixedWidth(120)
        self.entry.setPlaceholderText("Enter integer...")
        self.entry.returnPressed.connect(self._ins)
        r1_layout.addWidget(self.entry)
        
        self._add_btn(r1_layout, "Insert", self._ins, "primary")
        self._add_btn(r1_layout, "Delete", self._del, "secondary")
        self._add_btn(r1_layout, "Search", self._srch, "secondary")
        self._add_btn(r1_layout, "Bulk Insert", self._bulk, "secondary")
        
        r1_layout.addStretch()
        self._add_btn(r1_layout, "Clear Tree", self._clr, "secondary")
        self._add_btn(r1_layout, "Reset View", self._reset_view, "secondary")
        
        header_layout.addLayout(r1_layout)
        
        # Row 2: Traversals & Speed
        r2_layout = QHBoxLayout()
        r2_layout.setSpacing(10)
        r2_layout.addWidget(QLabel("Traversals:"))
        self._add_btn(r2_layout, "In-Order", lambda: self._trav('inorder'), "secondary")
        self._add_btn(r2_layout, "Pre-Order", lambda: self._trav('preorder'), "secondary")
        self._add_btn(r2_layout, "Post-Order", lambda: self._trav('postorder'), "secondary")
        
        r2_layout.addSpacing(20)
        r2_layout.addWidget(QLabel("Animation Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 800)
        self.speed_slider.setValue(250)
        self.speed_slider.setFixedWidth(200)
        self.speed_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        r2_layout.addWidget(self.speed_slider)
        r2_layout.addStretch()
        
        header_layout.addLayout(r2_layout)
        main_layout.addWidget(header)
        
        # Graphics View
        self.view = BSTGraphicsView(self.bst, self.layout_engine)
        self.view.setBackgroundBrush(QBrush(QColor('#000000')))
        
        # Change pen color for edges from #444444 to #FFFFFF
        # This will be done in the class below
        main_layout.addWidget(self.view)
        
        # Status Bar
        sf = QWidget()
        sf.setObjectName("StatusBar")
        sf_layout = QHBoxLayout(sf)
        sf_layout.setContentsMargins(16, 8, 16, 8)
        self.slbl = QLabel("Ready")
        self.slbl.setStyleSheet("color: #FFFFFF; font-weight: 600; background-color: transparent;")
        self.stplbl = QLabel("")
        self.stplbl.setStyleSheet("color: #AAAAAA; font-weight: 600; background-color: transparent;")
        sf_layout.addWidget(self.slbl)
        sf_layout.addStretch()
        sf_layout.addWidget(self.stplbl)
        main_layout.addWidget(sf)
        
        # Stats Bar
        stf = QWidget()
        stf.setObjectName("StatsBar")
        stf_layout = QHBoxLayout(stf)
        stf_layout.setContentsMargins(16, 6, 16, 6)
        self.statlbl = QLabel("")
        self.statlbl.setStyleSheet("color: #888888; font-size: 13px; background-color: transparent;")
        stf_layout.addWidget(self.statlbl)
        main_layout.addWidget(stf)

    def _add_btn(self, layout, text, cmd, btn_class):
        btn = QPushButton(text)
        btn.setProperty("btnClass", btn_class)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(cmd)
        layout.addWidget(btn)
        return btn

    def _redraw(self, hmap=None, rmap=None):
        self.view.full_redraw(hmap, rmap)
        self._stats()

    def _stats(self):
        n = len(self.bst.get_inorder())
        h = self.bst.get_height()
        bal = 'Yes' if self.bst.is_balanced() else 'No'
        s = str(self.bst.get_inorder())
        if len(s) > 60:
            s = s[:57] + '...'
        self.statlbl.setText(
            f'Nodes: {n}  |  Height: {h}  |  Balanced: {bal}  |  In-order: {s}'
        )

    def _st(self, msg):
        self.slbl.setText(msg)

    def _stp(self, msg):
        self.stplbl.setText(msg)

    def _reset_view(self):
        self.view.reset_view()

    def _ins(self):
        s = self.entry.text().strip()
        if not s:
            return
        try:
            val = int(s)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Please enter a valid integer.')
            return
        if self.bst.search(val):
            self._st(f'{val} already in tree')
            return
        self.entry.clear()
        self.bst.insert(val)
        self._st(f'Inserted {val}')
        self._stp('')
        seq = []
        for i in range(9):
            r = int(NODE_R * i / 8)
            h = {val: (CF_INS, CO_INS, 2)}
            rm = {val: r}
            seq.append((20, lambda h_=h, r_=rm: self._redraw(h_, r_)))
        seq.append((100, lambda: self._redraw({val: (CF_INS, CO_INS, 2)})))
        seq.append((400, lambda: self._redraw()))
        self.anim.enqueue(seq)

    def _del(self):
        s = self.entry.text().strip()
        if not s:
            return
        try:
            val = int(s)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Please enter a valid integer.')
            return
        if not self.bst.search(val):
            self._st(f'{val} not found')
            return
        self.entry.clear()
        self._st(f'Deleting {val}...')
        self._stp('')
        node = self.bst.search(val)
        has2 = bool(node.left and node.right)
        succ = self.bst.find_inorder_successor(val) if has2 else None
        seq = []

        def hl():
            hmap = {val: (CF_DEL, CO_DEL, 2)}
            if succ:
                hmap[succ.value] = (CF_FOUND, CO_FOUND, 2)
            self._redraw(hmap)

        seq.append((0, hl))
        if succ:
            seq.append((300, hl))
        for i in range(8, -1, -1):
            r = int(NODE_R * i / 8)

            def shrink(r_=r):
                hmap = {val: (CF_DEL, CO_DEL, 2)}
                if succ:
                    hmap[succ.value] = (CF_FOUND, CO_FOUND, 2)
                self.view.full_redraw(hmap, {val: r_})
                self._stats()

            seq.append((30, shrink))

        def commit():
            self.bst.delete(val)
            self._st(f'Deleted {val}')
            self._redraw()

        seq.append((0, commit))
        self.anim.enqueue(seq)

    def _srch(self):
        s = self.entry.text().strip()
        if not s:
            return
        try:
            val = int(s)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Please enter a valid integer.')
            return
        self._st(f'Searching {val}...')
        self._stp('')
        path, found = self.bst.search_with_path(val)
        seq = []
        visited = []
        for i, node in enumerate(path):
            def step(i_=i, n_=node, vis_=list(visited)):
                hmap = {v: (CF_PATH, CO_LEAF, 1) for v in vis_}
                hmap[n_.value] = (CF_FOUND, CO_FOUND, 2)
                self._redraw(hmap)
                self._stp(f'Step {i_+1}/{len(path)}')
            seq.append((250, step))
            visited.append(node.value)
        if found:
            def fin():
                hmap = {v: (CF_PATH, CO_LEAF, 1) for v in [n.value for n in path[:-1]]}
                hmap[found.value] = (CF_FOUND, CO_FOUND, 2)
                self._redraw(hmap)
                self._st(f'Found {val}')
                self._stp('')
            seq.append((600, fin))
            seq.append((0, lambda: self._redraw()))
        else:
            def nf():
                self._redraw()
                self._st(f'{val} not found')
                self._stp('')
                QMessageBox.information(self, 'Search', f'Value {val} not found in the tree.')
            seq.append((500, nf))
        self.anim.enqueue(seq)

    def _bulk(self):
        s = self.entry.text().strip()
        if not s:
            return
        try:
            vals = [int(v) for v in s.replace(',', ' ').split() if v.strip()]
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Enter integers separated by commas or spaces.')
            return
        self.entry.clear()
        count = 0
        for v in vals:
            if not self.bst.search(v):
                self.bst.insert(v)
                count += 1
        self._st(f'Bulk inserted {count} values')
        self._redraw()

    def _clr(self):
        self.anim.clear()
        self.bst.clear()
        self._st('Tree cleared')
        self._stp('')
        self._redraw()

    def _trav(self, mode):
        if not self.bst.root:
            self._st('Tree is empty')
            return
        if mode == 'inorder':
            nodes, label = self.bst.get_inorder_nodes(), 'In-Order'
        elif mode == 'preorder':
            nodes, label = self.bst.get_preorder_nodes(), 'Pre-Order'
        else:
            nodes, label = self.bst.get_postorder_nodes(), 'Post-Order'
        self._st(f'{label} traversal...')
        seq = []
        visited = []
        for i, node in enumerate(nodes):
            def step(i_=i, n_=node, vis_=list(visited)):
                hmap = {v: (CF_TVIS, CO_TVIS, 1) for v in vis_}
                hmap[n_.value] = (CF_TCUR, CO_TCUR, 2)
                self._redraw(hmap)
                self._stp(f'{label} {i_+1}/{len(nodes)}: {n_.value}')
            seq.append((self.speed_slider.value() if i > 0 else 0, step))
            visited.append(node.value)

        def done():
            self._redraw()
            self._st(f'{label} complete')
            self._stp('')

        seq.append((600, done))
        self.anim.enqueue(seq)


def main():
    app = QApplication(sys.argv)
    window = BSTVisualizerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
