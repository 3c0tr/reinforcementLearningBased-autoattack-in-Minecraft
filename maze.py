import torch
import random
import socket
import time
import pygetwindow as gw
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from PyQt5.QtWidgets import QApplication
import numpy as np
import cv2
import sys
import win32gui
import classgame

m = PyMouse()
k = PyKeyboard()
yololo = classgame.mygame()
print("yolo done")
c = socket.socket()
host = '127.0.0.1'
port = 2000
c.connect((host,port))
app = QApplication(sys.argv)
screen=QApplication.primaryScreen()

class modell(torch.nn.Module):
    def  __init__(self) -> None:
        super().__init__()

        self.i1 = torch.nn.Sequential(
                torch.nn.Linear(2,256),
                torch.nn.ReLU(),
                torch.nn.Linear(256,7),
                torch.nn.Sigmoid()
                 )
       
    def forward(self,x):
        x = self.i1(x)
        x = x + (torch.ones(x.shape) * 0.02)
        return x

model = modell()

model_td = torch.nn.Sequential(
    torch.nn.Linear(2,128),
    torch.nn.ReLU(),
    torch.nn.Linear(128,1)
)


def fromMinecraft(data):
    px, py, reward = 0, 0, 0
    if data.find("Zombie") != -1:
        print("a Zombie was killed")
        reward += 25
    if data.find("You") != -1:
        print("you been killed")
        reward += 0
    if data.find("px:") != -1:
        px = (int)(data[data.find("px:")+3:data.find("px:")+7])
        if px < 20:
            reward += px
        print("Do damage " + str(px))
    if data.find("py:") != -1:
        py = (int)(data[data.find("py:")+3:data.find("py:")+7])
        reward -= py
        print("Get damage -" + str(py))
    return reward

def get_action(state, model):
    w, a, s, d, q, e, attack = False, False, False, False, False, False, False

    state = torch.FloatTensor(state).reshape(1,2)
    out = model(state)# + randomtendz
    
    if out[0,0] > random.random():
        w = True
    if out[0,1] > random.random():
        a = True
    if out[0,2] > random.random():
        s = True
    if out[0,3] > random.random():
        d = True
    if out[0,4] > random.random():
        q = True
    if out[0,5] > random.random():
        e = True
    if out[0,6] > random.random():
        attack = True
    
    return w, a, s, d, q, e, attack

def toMinecraft(w, a, s, d, q, e, attack):
    k.press_key("w") if w else k.release_key("w")
    k.press_key("a") if a else k.release_key("a")
    k.press_key("s") if s else k.release_key("s")
    k.press_key("d") if d else k.release_key("d")
    if q:
        m.move(m.position()[0] - 11, m.position()[1])
    if e:
        m.move(m.position()[0] + 11, m.position()[1])
    if attack:
        #m.click(m.position()[0], m.position()[1], 2, 1)
        m.press(m.position()[0], m.position()[1], 1)
    else:
        m.release(m.position()[0], m.position()[1], 1)


def fromIMG(reward):
    hwnd = win32gui.FindWindow(None, gw.getActiveWindowTitle())
    mobThread = 0
    closestPosition = 0
    if hwnd != None:
        img=screen.grabWindow(hwnd).toImage()
        ptr = img.constBits()
        ptr.setsize(img.byteCount())
        mat = np.array(ptr).reshape(img.height(), img.width(), 4)
        mat = np.delete(mat, 3, 2)
        pred = yololo.pred(mat)
        if pred[0] != None:
            for mob in pred[0]:
                if mob[3] - mob[1] > mobThread:
                    mobThread = mob[3] - mob[1]
                    closestPosition = ((mob[0] + mob[2]) / 2) - 208
                    closestPosition = closestPosition.cpu().numpy()
            reward += 5/(abs(closestPosition) + 1)
    return mobThread, closestPosition, reward 

def update_data():
    states = []
    rewards = []
    actions = []
    next_states = []
    while gw.getActiveWindowTitle().find("Minecraft") == -1:
        time.sleep(0.1)
    reward = fromMinecraft(c.recv(2048).decode())
    mobThread, closestPosition, reward = fromIMG(reward)
    state = [mobThread, closestPosition]

    while len(states) < 200:
        if gw.getActiveWindowTitle().find("Minecraft") != -1:
            reward = fromMinecraft(c.recv(2048).decode())
            mobThread, closestPosition, reward = fromIMG(reward)
            next_state = [mobThread, closestPosition]
            w, a, s, d, q, e, attack = get_action(state, model)
            if attack:
                reward -= 2
            action = [w, a, s, d, q, e, attack]
            toMinecraft(w, a, s, d, q, e, attack)
            
            states.append(state)
            rewards.append(reward)
            actions.append(action)
            next_states.append(next_state)
            state = next_state
            time.sleep(0.02)
    states = torch.FloatTensor(states).reshape(-1, 2)
    rewards = torch.FloatTensor(rewards).reshape(-1, 1)
    actions = torch.LongTensor(actions).reshape(-1, 7)
    next_states = torch.FloatTensor(next_states).reshape(-1, 2)

    return states, rewards, actions, next_states
    
def get_advantages(deltas):
    advantages = []
    s = 0.0
    for delta in deltas[::-1]:
        s = 0.98 * 0.95 * s + delta
        advantages.append(s)
    
    advantages.reverse()
    return advantages

def train():
    model.train()
    optimzer = torch.optim.Adam(model.parameters(), lr = 0.02)
    optimzer_td = torch.optim.Adam(model_td.parameters(), lr = 0.02)
    loss_l = torch.nn.L1Loss()
    loss_fn = torch.nn.MSELoss()

    for epoch in range(100):
        print("updateing epoch:" + str(epoch) + "")
        torch.set_grad_enabled(False)
        states, rewards, actions, next_states = update_data()
        torch.set_grad_enabled(True)

        k.tap_key(k.escape_key)
        
        values = model_td(states)

        targets = model_td(next_states).detach()
        targets *= 0.98
        targets += rewards

        deltas = (targets - values).squeeze(dim = 1).tolist()
        advantages = get_advantages(deltas)
        advantages = torch.FloatTensor(advantages).reshape(-1, 1)

        old_probs = model(states)
        old_probs = old_probs.gather(dim = 1, index = actions)
        old_probs = old_probs.detach()

        for _ in range(10):
            new_probs = model(states)
            new_probs = new_probs.gather(dim = 1, index = actions)
            new_probs = new_probs

            ratios = new_probs / old_probs

            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 0.8, 1.2) * advantages
            loss = -torch.min(surr1, surr2)
            loss = loss.mean()

            values = model_td(states)
            loss_td = loss_fn(values, targets)
            with torch.autograd.detect_anomaly():
                optimzer.zero_grad()
                loss.backward()
                optimzer.step()

                optimzer_td.zero_grad()
                loss_td.backward()
                optimzer_td.step()

        k.tap_key(k.escape_key)
        torch.save(model, "b1.pt")
        torch.save(model_td, "b1_td.pt")

if True:
    model = torch.load("b2.pt")
    model_td = torch.load("b2_td.pt")
    train()
    #torch.save(model, "b1.pt")
    #torch.save(model_td, "b1_td.pt")

    print("stoped")
    torch.set_grad_enabled(False)
        
    while True:
        if gw.getActiveWindowTitle().find("Minecraft") != -1:
            hwnd = win32gui.FindWindow(None, gw.getActiveWindowTitle())
            if hwnd != None:
                mobThread, closestPosition, reward = fromIMG(fromMinecraft(c.recv(2048).decode()))
                state = [mobThread, closestPosition]
                w, a, s, d, q, e, attack = get_action(state, model)
                action = [w, a, s, d, q, e, attack]
                toMinecraft(w, a, s, d, q, e, attack)
            time.sleep(0.05)
