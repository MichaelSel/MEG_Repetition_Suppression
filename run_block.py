from psychopy import visual, core
from psychopy.sound import Sound
import psychopy
import pandas as pd
from port_open_send import sendTrigger
'''Set Task set'''
task_set = "MEGp2000"

'''Set DEFAULTS'''
psychopy.prefs.hardware['audioLib'] = ['PTB', 'pyo','pygame','sounddevice']
default_ITI = 1 #seconds
task_set_path = './task_sets/' + task_set
task_set_csv_dir = task_set_path + "/csv"
task_audio_dir = task_set_path + "/audio"

'''Track EVENTS'''
all_events=[]

choice_mapping = {
    'a': {'name':'option 1','order':0},
    'l': {'name':'option 2','order':1}
}


def open_window(size=None):
    all_events.append({'what':"window open",'when':core.getTime()-experiment_start,'content':None,'response':None})
    if(size): return visual.Window(size,color=[0,0,0])
    return visual.Window(fullscr=True,color=[0,0,0])

def show_message(msg="",keys=None,context="",store=True):
    all_events.append(
        {'what': "message displayed", 'when': core.getTime() - experiment_start, 'content': msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys!=None):
        print(all_keys)
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()

    key = psychopy.event.waitKeys(keyList=keys)




    if(store):all_events.append({'what': "keypress", 'when': core.getTime() - experiment_start, 'content': None, 'response': key,
                       'context': context})
    return key
def choice_screen(keys=None,trigger_port=None):
    all_events.append(
        {'what': "choice_screen", 'when': core.getTime() - experiment_start, 'content': "", 'response': None})
    msg = "Which of the two comparison melodies (Option 1 or Option 2) sounded more DIFFERENT than the test melody?"
    option1 = "[A] Option 1 was more different"
    option2 = "[L]Option 2 was more different"
    msg = visual.TextStim(win, text=msg)
    option1 = visual.TextStim(win, text=option1)
    option1.pos = (-0.5, -0.5)
    option2 = visual.TextStim(win, text=option2)
    option2.pos = (0.5, -0.5)
    msg.draw()
    option1.draw()
    option2.draw()
    win.flip()
    if(trigger_port):
        sendTrigger(trigger_port, duration=0.01)
        print("sending trigger for choice screen")

    # escape code
    all_keys = psychopy.event.getKeys()
    if (all_keys!=None):
        if 'b' in all_keys and 'p' in all_keys:
            core.quit()


    key = psychopy.event.waitKeys(keyList=keys)
    return key
def timed_message(msg="",time=1):
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
def play_file(path,msg,trigger_port,trigger_twice=False):
    all_events.append(
        {'what': "audio played", 'when': core.getTime() - experiment_start, 'content': path, 'message':msg, 'response': None})
    msg = visual.TextStim(win, text=msg)
    msg.draw()
    win.flip()
    mySound = Sound(path)
    if (trigger_port):
        sendTrigger(trigger_port, duration=0.01)
        print("sending trigger for audio start")
    mySound.play()
    core.wait(mySound.getDuration())
    if (trigger_port and trigger_twice):
        sendTrigger(trigger_port, duration=0.01)
        print("sending trigger for audio end")
def start_experiement(size=None):
    '''Experiement Start'''
    all_events.append(
            {'what': "experiement start", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    if(size): return open_window(size)
    return open_window()

def choice_trial(entry,num_of_Qs=25):
    show_message("Block {}, Question {} of {}\nPress any key to hear the test melody and the two comparison melodies.".format(entry['block_num'],entry['question_in_block'],num_of_Qs))
    timed_message("3...", 1)
    timed_message("2...", 1)
    timed_message("1...", 1)
    play_file("{}/{}".format(task_audio_dir,entry['probe_file']),"Test Melody",trigger_port=f'ch160',trigger_twice=True)
    show_ITI()
    play_file("{}/{}".format(task_audio_dir, entry['option1_file']), "Option 1",trigger_port=f'ch161')
    show_ITI()
    play_file("{}/{}".format(task_audio_dir, entry['option2_file']), "Option 2",trigger_port=f'ch161')
    show_ITI()
    choice = choice_screen(choice_mapping.keys(),trigger_port=f'ch161')
    sendTrigger(f'ch161') #trigger when subject responsed
    print("sending trigger used response")
    choice = choice[0]
    all_events.append(
        {
            'what': "choice_response",
            'when': core.getTime() - experiment_start,
            'char':choice,
            'choice':choice_mapping[choice]['name'],
            'preferred': entry['order'].split(',')[choice_mapping[choice]['order']],
            'Q_in_Block':entry['question_in_block'],
            'Q_in_task': entry['question_in_task'],
            'probe_pitches': entry['probe'],
            'swapped_pitches': entry['swapped'],
            'shifted_pitches': entry['shifted'],
            'shift_amount': entry['shift_amount'],
            'shift_position': entry['shift_position'],
            'set': entry['set'],
            'order': entry['order'].split(','),
            'mode': entry['mode'],
            'mode_num': entry['mode_num'],
            'transposition': entry['transposition'],
            'probe_file': entry['probe_file'],
            'option1_file': entry['option1_file'],
            'option2_file': entry['option2_file'],
        })
def run_block(block_num,show_instrctions_on_1=True):
    experiment_start = core.getTime() #reset timer to the beginning of the block
    all_events.append(
        {'what': "block {} start".format(block_num), 'when': core.getTime() - experiment_start, 'content': None, 'response': None})

    csv = load_block_csv(block_num).to_dict('records')

    if(block_num==1 and show_instrctions_on_1):
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
    for row in csv:

        choice_trial(row,len(csv))
        save_event_data('trial_data_block_{}.json'.format(block_num)) #save after every response

    # save_event_data('trial_data_block_{}.json'.format(block_num)) #save at the end of each block
    all_events.append(
        {'what': "block {} end".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    end_experiement()
def end_experiement():
    all_events.append({'what': "experiement end", 'when': core.getTime() - experiment_start, 'content': None, 'response': None})
    win.close()
def load_block_csv(block_num):
    csv = pd.read_csv("{}/block_{}.csv".format(task_set_csv_dir,block_num))
    all_events.append(
        {'what': "block {} csv loaded".format(block_num), 'when': core.getTime() - experiment_start, 'content': None,
         'response': None})
    return csv
def save_event_data(filename):
    data = pd.DataFrame(all_events)
    data['time_since_last_event'] =  data['when'] - data['when'].shift(1)
    data.to_json(task_set_csv_dir + "/" + filename,orient='records')







experiment_start = core.getTime()
win = start_experiement([800,800])

run_block(1)


