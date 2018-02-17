import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import WebKit2
from os.path import join
from os.path import abspath
from os.path import dirname

import markdown
from steem.steemd import Steemd


steemd_nodes = [
    "https://api.steemit.com",
    "https://gtg.steem.house:8090",
    "https://steemd.minnowsupportproject.org",
    "https://steemd.privex.io",
    "https://rpc.steemliberator.com",
]

std = Steemd(nodes=steemd_nodes)

HERE = abspath(dirname(__file__))

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

class Steemplay(object):

    def __init__(self):
        self.setupGUI()
        self.oldest_entry = 0
        self.feed = []

    def setupGUI(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(HERE, "steemplay.ui"))
        self.builder.connect_signals(self)

        get_obj = self.builder.get_object
        self.window = get_obj("window")
        self.window.connect('delete-event', Gtk.main_quit)

        self.content_webview = WebKit2.WebView()
        content_scrolled = get_obj("content_scrolled")
        content_scrolled.add_with_viewport(self.content_webview)

        self.window.show_all()

        self.listbox = get_obj("listbox")
        self.hb = get_obj("headerbar")

        self.btn_vote = get_obj("btn_vote")

    def onButtonPressed(self, widget):
        self.update_new()

    def onRowSelected(self, listbox, listboxrow):
        i = listboxrow.get_index()
        print(i)
        self.update_content(i)

    def update_new(self):
        new_feed = std.get_feed("dereisele", self.oldest_entry, 6)

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

    def update_content(self, id):
        content = self.feed[id]["comment"]["body"]
        title = self.feed[id]["comment"]["title"]
        author = self.feed[id]["comment"]["author"]
        votes = self.feed[id]["comment"]["net_votes"]
        html = markdown.markdown(text=content, output_format="html5")
        self.content_webview.load_html(html, "")
        self.hb.set_title(title)
        self.hb.set_subtitle(author)
        self.btn_vote.set_label(str(votes))


if __name__ == "__main__":
    win = Steemplay()
    Gtk.main()
