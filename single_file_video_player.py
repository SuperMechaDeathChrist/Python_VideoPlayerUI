import PySimpleGUI as sg
import vlc
import os

B = sg.Button  # Buttons
T = sg.T  # Text element
Canvas = sg.Canvas  # Canvas element

icon_open_new = b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAbrkAAG65AXtnkHoAAAF6SURBVHhe7ZpRioMwFEXjLMAPlyH4L+jyFfwXugw/3IDDlduAGKvTcZg09x0ot6lQyDHvRW2zZVmcMl9MWUwAUxb0gL9oAhkzeqwEmHfzMVvLpgSmaXKPx4Oj65Rl6Yqi4GhD9KXgBWDywzC4cRzXAz+haRrXti1HG6IX4EsAZ/6dyYN5nleBASA3pteOW3oAxGH1HEiIiZ2E25rgp0rwPaDrOtf3/frhb6iqyuV5ztH/cqU53y4gJnAy6roOSfACkr4QQlmebetJC7jCaQnEVNPvcNYHDgU8J/7iC1IgC5bAs3ng6i7hyYMlKABnPvGJe+SboAlgelD/aHwq7AQo1T+wEmDKYgKYsmyeCeLOKfFL3x1egCjhewElTABTFhPAVGR9ImQrgCmLCWDKoipA45ehK5gApiwmgCmLogC/AwBbAUxZTABTFjUBmwYIbAUwZTEBTFlMAFOB3Q4AbAUwZVEREFz+AAIODybCy/nh/wF8q4n1AKYozn0Digah3lSTYkAAAAAASUVORK5CYII='
################################################
# You may need to parse and validate the path for the video

def valid_path(file_path):
    # this is necesary on windows
    return file_path.replace('/', '\\')

################################################
# For Fullscreen purposes
from win32api import GetSystemMetrics
Width = GetSystemMetrics(0)
Height = GetSystemMetrics(1)

################################################
# set the player with the bindings to the vlc player
Instance = vlc.Instance("--no-xlib")
player = Instance.media_player_new()


################################################
# every media file needs to be set in the player
def set_media(player, mediapath):
    # this is for local files
    Media = Instance.media_new_path(mediapath)
    player.set_media(Media)

################################################
# Making User Interfaces with PySimpleGUI is the fastest and easiest way I know

Title = 'PlayerPy'
vide_default_size = (640, 480)

button_color = ('white', 'black')
font = ('Forque', '11')

is_full = False  # Window fullscreen flag
file_path = ''

# you may need to change these acording to your operating system, this is what
# shows up in the keyboard events when I press combined keys
ESC = ''
CTRL_O = ''
SPACE = ' '
################################################
# A simple layout
layout = [[B(' ⬛ ', key='stop', tooltip='stop',
             button_color=button_color, font=font),
           B(' ►', key='pause', tooltip='pause/unpause\n(SPACE)',  # focus=True,
             button_color=button_color, size=(
                 3, 1), auto_size_button=False, font=font),
           B('『+』', tooltip='fullscreen\n(F11)', key='full',
             button_color=button_color, font=font),
           B('', image_data=icon_open_new, image_subsample=3, key='open', button_color=button_color, image_size=(45, 25),
             font=font, tooltip='open new file\n(CTRL+O)'),
           T('Vol: ' + str(player.audio_get_volume()), justification='right', text_color='white', size=(Width, 1),
             key='Vol', tooltip='Volume: (RePag/AvPag)\n∓5 seconds: (Left/Right)', background_color='black'),
           ],
          [Canvas(key='video_canvas', tooltip='Volume: (RePag/AvPag)\n∓5 seconds: (Left/Right)',
                  background_color='black', size=(Width, Height))
           ],
          ]

################################################
# Build the window
window = sg.Window(title=Title,
                   # keep_on_top=True,
                   resizable=True,
                   use_default_focus=False,
                   # disable_minimize=True,
                   return_keyboard_events=True,
                   background_color='black',
                   element_padding=(0, 0),
                   grab_anywhere=True).Layout(layout).Finalize()
window.Size = vide_default_size
window.TKroot.focus_force() # force the window to the front
################################################
# This is all you need to embed the player into the GUI
video_canvas = window['video_canvas'].TKCanvas
player.set_hwnd(video_canvas.winfo_id())

################################################
# Start the program loop
while True:
    event, values = window.Read(timeout=500, timeout_key='timeout')
    #print(event, values, sep='\n')

    if event is None:
        if player.is_playing():
            player.stop()
        window.Close()
        break

    elif 'F11' in event or event in ['full', ESC]:
        # fullscreen
        if is_full:
            window.TKroot.attributes('-fullscreen', False) # restores the window
            window['full'](text='『+』')
            is_full = False

        elif not is_full and not event is ESC:
            window['video_canvas'].TKCanvas.config(
                width=Width, height=Height)
            window.TKroot.attributes('-fullscreen', True) # fullscreen mode
            window.Move(0, 0)
            window['full'](text='『−』')
            is_full = True

    elif event in [CTRL_O, 'open']:
        player.stop()

        # you can actually play all the supported video/music formats by vlc...
        new_file_path = sg.PopupGetFile('Open media files', no_window=True, file_types=[
            ('Media files', '*.mp3 *.mp4'), ])  # ...but I'm lazy writing
        window.TKroot.focus_force()

        if new_file_path:

            file_path = valid_path(new_file_path)
            set_media(player, file_path)
            player.play()
            window['pause'](text=' ▍▍')
            window.TKroot.title(Title + ' - ' + os.path.basename(file_path)) # renames your window

    elif event is 'stop':
        # stop
        player.stop()
        if player.is_playing():
            window['pause'](text=' ►')
    elif event in ['pause', SPACE]:
        # pause/unpause
        if not player.is_playing() and file_path:
            player.play()

        if player.is_playing():
            window['pause'](text=' ►')
            player.pause()
        elif file_path:
            window['pause'](text=' ▍▍')

    elif 'Right' in event:
        # time +5 seconds
        ctime = player.get_time()
        player.set_time(ctime + 5000)
    elif 'Left' in event:
        # time -5 seconds
        ctime = player.get_time()
        player.set_time(ctime - 5000)
    elif 'Up' in event:
        # volume +5 db
        cvol = player.audio_get_volume() + 5
        if cvol < 151:
            player.audio_set_volume(cvol)
            window['Vol']('Vol: ' + str(cvol))
    elif 'Down' in event:
        # volume -5 db
        cvol = player.audio_get_volume() - 5
        if cvol > -1:
            player.audio_set_volume(cvol)
            window['Vol']('Vol: ' + str(cvol))
    elif event is 'timeout':
        if not player.is_playing() and window['pause'].GetText() is ' ▍▍':
            player.stop()
            window['pause'](text=' ►')
