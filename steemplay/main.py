import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import WebKit2

import markdown
from steem.steemd import Steemd


steemd_nodes = [
    'https://gtg.steem.house:8090',
]

def big(text):
    return "<big>" + text + "</big>"


class ListBoxRowItem(Gtk.ListBoxRow):
    def __init__(self, entry_id, author, title):
        super(Gtk.ListBoxRow, self).__init__()

        self.entry_id = entry_id

        label_author = Gtk.Label(author)
        label_title = Gtk.Label()

        label_title.set_markup(big(title))
        label_title.set_line_wrap(True)

        separ = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        box.pack_start(label_author, True, True, 0)
        box.pack_start(label_title, True, True, 0)
        box.pack_end(separ, False, False, 0)

        self.add(box)

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Steemplay")
        self.addWidgets()
        self.setupSteem()
        self.oldest_entry = 0
        self.feed = []

    def addWidgets(self):

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        ## HEADER BAR
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = "Steemplay"
        self.set_titlebar(self.hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self.hb.pack_start(button)

        button.connect("clicked", self.on_button_clicked)

        ## LIST WINDOW
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row_activated", self.on_row_activated)

        list_window = Gtk.ScrolledWindow()
        #list_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        list_window.add(self.listbox)

        ## CONTENT WINDOW
        self.content_webview = WebKit2.WebView()

        content_window = Gtk.ScrolledWindow()
        content_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        content_window.add(self.content_webview)

        ## MAIN BOX
        paned.pack1(list_window, True, False)
        paned.pack2(content_window, True, False)
        paned.set_position(100)

        self.add(paned)

    def setupSteem(self):
        self.std = Steemd(nodes=steemd_nodes)

    def on_button_clicked(self, widget):
        self.update_new()

    def on_row_activated(self, listbox, listboxrow):
        i = listboxrow.get_index()
        print(i)
        self.update_webview(i)

    def update_new(self):
        new_feed = self.std.get_feed("dereisele", self.oldest_entry, 6)

        if new_feed == None:
            print("Feed is None")
            return

        print("oldest_entry", self.oldest_entry)
        self.oldest_entry = new_feed[-1]["entry_id"] -1
        self.feed.extend(new_feed)

        for f in new_feed:
            author = f["comment"]["author"]
            title = f["comment"]["title"]
            entry_id = f["entry_id"]

            row = ListBoxRowItem(entry_id, author, title)
            self.listbox.add(row)

        self.listbox.show_all()

    def update_webview(self, id):
        content = self.feed[id]["comment"]["body"]
        title = self.feed[id]["comment"]["title"]
        author = self.feed[id]["comment"]["author"]
        html = markdown.markdown(text=content, output_format="html5")
        self.content_webview.load_html(html, "")
        self.hb.set_title(title)
        self.hb.set_subtitle(author)


if __name__ == "__main__":
    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
