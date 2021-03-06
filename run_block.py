from psychopy import visual, core, monitors
import psychopy

psychopy.prefs.hardware['audioLib'] = ['PTB', 'pyo', 'pygame', 'sounddevice']
from psychopy.sound import Sound
import pandas as pd
from port_open_send import sendTrigger

'''Set Task set'''
task_set = "sVgMEG0000"

# TO-DO: add if already in data folder, throw error

'''Set DEFAULTS'''
default_ITI = 1  # in seconds
task_set_path = './task_sets/' + task_set
task_set_csv_dir = task_set_path + "/csv"
task_audio_dir = task_set_path + "/audio"
experiment_start = core.getTime()
screen = 1  # which screen/monitor to use
win = None  # will store window object
'''Track EVENTS: i.e., all data stored here'''
all_events = []

choice_mapping = {
    'a': {'name': 'option 1', 'order': 0},
    'l': {'name': 'option 2', 'order': 1},
    'None': {'name': "None", 'order': None},
}


def run_block(block_num, show_instrctions_on_1=True):
    all_events = []  # reset events

    experiment_start = core.getTime()  # reset timer to the beginning of the block
    all_events.append(
        {'what': "block {} start".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})

    csv = load_block_csv(block_num).to_dict('records')

    if block_num == 1 and show_instrctions_on_1:
        show_message("Hello and welcome to the study.\nPress any key on your keyboard to continue.")

        show_ITI()

    show_message("For every trial you will listen to a (\"test\") melody.\n" +
                 "This melody will be followed by two similar (\"comparison\") melodies (Option 1 and Option 2).\n" +
                 "Press any key on your keyboard to continue.")
    show_ITI()
    show_message("After listening to the melodies, you will be asked to pick one" +
                 "of the two comparison melodies that (in your opinion) sounds" +
                 "most DIFFERENT than the original test melody." +
                 "If you think Option 1 was more different than the test melody, please press [A] on your keyboard.\n" +
                 "Otherwise, if you think Option 2 was MORE DIFFERENT than the test, please press [L] on your keyboard.\n" +
                 "Press any key on your keyboard to continue.")
    show_ITI()
    show_message("Please pay attention to the cross at the center of the screen throughout the task.\n" +
                 "Press any key on your keyboard to continue.")

    show_message("Experimental Block {} of 10\n Press any key to continue.".format(block_num))

    # loop through trial information in block
    for row in csv:
        choice_trial(row, num_of_Qs=len(csv))
        save_event_data('trial_data_block_{}.json'.format(block_num))  # save after every response

    # save_event_data('trial_data_block_{}.json'.format(block_num)) #save at the end of each block
    all_events.append(
        {'what': "block {} end".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    end_experiment()


def open_window(size=None):
    all_events.append(
        {'what': "window open", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    if (size): return visual.Window(size, color=[-1], screen=screen)
    return visual.Window(fullscr=True, color=[-1], screen=screen)


def show_message(msg="", keys=None, context="", store=True):
    all_events.append(
        {'what': "message displayed", 'when': core.getTime() - experiment_start, 'content': msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys != None):
        print(all_keys)
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()

    key = psychopy.event.waitKeys(keyList=keys)

    if (store): all_events.append(
        {'what': "keypress", 'when': core.getTime() - experiment_start, 'content': None, 'response': key,
         'context': context})
    return key


def choice_screen(keys=None, trigger_port=None, time_limit=None):
    all_events.append(
        {'what': "choice_screen", 'when': core.getTime() - experiment_start, 'content': "", 'response': None})
    msg = "Which of the two candidate melodies (Option 1 or Option 2) sounded more REPETITIVE?"
    option1 = "[A] Option 1 was more different"
    option2 = "[L] Option 2 was more different"
    msg = visual.TextStim(win, text=msg)
    option1 = visual.TextStim(win, text=option1)
    option1.pos = (-0.5, -0.5)
    option2 = visual.TextStim(win, text=option2)
    option2.pos = (0.5, -0.5)
    msg.draw()
    option1.draw()
    option2.draw()
    rect = visual.Rect(win, width=100)
    rect.draw()

    win.flip()

    if (trigger_port):
        sendTrigger(trigger_port, duration=0.01)

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys != None):
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()

    key = []
    if(time_limit):
        timer = core.Clock()
        timer.add(time_limit)
        while timer.getTime() < 0 and len(key)==0:
            key = psychopy.event.getKeys(keyList=keys)
            msg.draw()
            option1.draw()
            option2.draw()
            fill = psychopy.visual.Rect(
                win=win,
                units="pix",
                width=750 * (abs(timer.getTime())/time_limit),
                height=100,
                fillColor=[1, -1, -1],
                pos=(0, -400)
            )
            fill.draw()
            win.flip()
    else:
        key = psychopy.event.waitKeys(keyList=keys)
    return key


def timed_message(msg="", time=1):
    all_events.append(
        {'what': "timed message", 'when': core.getTime() - experiment_start, 'content': msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()
    core.wait(time)


def show_ITI(time=default_ITI):
    all_events.append(
        {'what': "ITI", 'when': core.getTime() - experiment_start, 'content': time, 'response': None})
    ITI = visual.TextStim(win, text="+")
    ITI.draw()
    win.flip()
    core.wait(time)


def play_file(path, msg, trigger_port, trigger_twice=False):
    all_events.append(
        {'what': "audio played", 'when': core.getTime() - experiment_start, 'content': path, 'message': msg,
         'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()
    mySound = Sound(path)
    if (len(trigger_port)>0):
        for port in trigger_port:
            sendTrigger(port, duration=0.01)

    mySound.play()
    core.wait(mySound.getDuration())
    if (len(trigger_port)>0 and trigger_twice):
        for port in trigger_port:
            sendTrigger(port, duration=0.01)


def start_experiment(size=None):
    '''Experiement Start'''
    all_events.append(
        {'what': "experiement start", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    if (size): return open_window(size)
    return open_window()


def choice_trial(entry, num_of_Qs):
    show_message(
        "Block {}, Question {} of {}\nPress any key to hear the two candidate melodies.".format(
            entry['block_num'], entry['question'], num_of_Qs))
    timed_message("3...", 1)
    timed_message("2...", 1)
    timed_message("1...", 1)



    triggers = {
        'option1': f'ch160', #trigger at audio start of option 1
        'option2': f'ch161', #trigger at audio start of option 2
        'chromatic': f'ch162', #trigger at audio start of the chromatic option (in addition to order trigger)
        'diatonic': f'ch163', #trigger at audio start of the diatonic option (in addition to order trigger)
        'choice_appear': f'ch164',  # trigger once choice screen appears
        'responded': f'ch165' # trigger once subject responded to choice screen
    }


    play_file("{}/{}".format(task_audio_dir, entry['option1_file']), "Option 1", trigger_port=[triggers['option1'],triggers[entry['order'].split(',')[0]]])
    show_ITI()
    play_file("{}/{}".format(task_audio_dir, entry['option2_file']), "Option 2", trigger_port=[triggers['option2'],triggers[entry['order'].split(',')[1]]])
    show_ITI()
    choice = choice_screen(choice_mapping.keys(), trigger_port=triggers['choice_appear'],time_limit=3)
    sendTrigger(triggers['responded'])  # trigger when subject responsed
    print(choice)
    if(len(choice)>0): choice = choice[0]
    else: choice = "None"



    all_events.append(
        {
            'what': "choice_response",
            'when': core.getTime() - experiment_start,
            'char': choice,
            'choice': choice_mapping[choice]['name'],
            'preferred': (entry['order'].split(',')[choice_mapping[choice]['order']]) if choice!="None" else choice,
            'Q_in_Block': entry['question'],
            'block': entry['block_num'],
            'diatonic_pitches':entry['diatonic'],
            'chromatic_pitches': entry['chromatic'],
            'necklace':entry['necklace'],
            'scale':entry['scale'],
            'mode_num':entry['mode'],
            'fragment_generic': entry['fragment_generic'],
            'fragment_specific': entry['fragment_specific'],
            'fragment_span':entry['fragment_span'],
            'option1':entry['order'].split(',')[0],
            'option2': entry['order'].split(',')[1],
            'transposition':entry['transposition'],
            'fragment_file':entry['fragment_file'],
            'option1_file': entry['option1_file'],
            'option2_file': entry['option2_file'],
        })


def end_experiment():
    all_events.append(
        {'what': "experiement end", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    win.close()


def load_block_csv(block_num):
    csv = pd.read_csv("{}/block_{}.csv".format(task_set_csv_dir, block_num))
    all_events.append(
        {'what': "block {} csv loaded".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    return csv


def save_event_data(filename):
    data = pd.DataFrame(all_events)
    data['time_since_last_event'] = data['when'] - data['when'].shift(1)
    data.to_json(task_set_csv_dir + "/" + filename, orient='records')


win = start_experiment()  # [800, 800]

run_block(1)  # uncomment to run the block
