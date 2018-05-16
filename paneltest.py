from time import sleep
import curses, curses.panel

def make_panel(h,l, y,x, str):
 win = curses.newwin(h,l, y,x)
 win.erase()
 win.box()
 win.addstr(2, 2, str)

 panel = curses.panel.new_panel(win)
 return win, panel

def test(stdscr):
 try:
  curses.curs_set(0)
 except:
  pass
 stdscr.box()
 stdscr.addstr(2, 2, "panels everywhere")
 stdPanel = curses.panel.new_panel(stdscr)
 win1, panel1 = make_panel(10,12, 5,5, "Panel 1")
 win2, panel2 = make_panel(10,12, 8,8, "Panel 2")
 curses.panel.update_panels(); stdscr.refresh()
 panel1.hide()
 curses.panel.update_panels()
 stdscr.refresh()
 sleep(1)
 panel1.top(); curses.panel.update_panels(); stdscr.refresh()
 sleep(1)

 for i in range(20):
  panel2.move(8, 8+i)
  curses.panel.update_panels()
  stdscr.refresh()
  sleep(0.1)

 panel1.hide()
 curses.panel.update_panels()
 curses.doupdate()
 sleep(1)
 win1.addstr(2, 2, "changed")
 win1.noutrefresh()
 if not panel1.hidden():
    stdscr.refresh()
 sleep(1)
 panel1.show()
 curses.panel.update_panels()
 curses.doupdate()
 curses.flash()
 sleep(1)

if __name__ == '__main__':
 curses.wrapper(test)