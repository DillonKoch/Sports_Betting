# example 1
import tkinter as tk

root = tk.Tk()

w = tk.Label(root, text="waddup tho... CJ Beathard, watch this")
w.pack()

root.mainloop()


# example 2
text = """waddup tho, my name is
CJ Beathard,
watch this..."""

root = tk.Tk()
logo = tk.PhotoImage(file='Python.png')
w1 = tk.Label(root, image=logo).pack(side="left")
w2 = tk.Label(root, justify=tk.LEFT, padx=1,
              text=text).pack(side='left')
root.mainloop()

# example 3 - compound
root = tk.Tk()
logo = tk.PhotoImage(file='Python.png')
text = """waddup tho, my name is
CJ Beathard,
watch this..."""
w = tk.Label(root, compound=tk.CENTER, text=text,
             image=logo).pack(side='top')
root.mainloop()

root = tk.Tk()
logo = tk.PhotoImage(file='Python.png')
text = """waddup tho, my name is
CJ Beathard, 
watch this..."""
w = tk.Label(root, justify=tk.LEFT, compound=tk.TOP,
             padx=10, text=text, image=logo).pack(side='right')
root.mainloop()

# example 4 - changing up the fonts and colors
root = tk.Tk()
text = "Packers (-2.5) at Seahawks"
w = tk.Label(root, text=text, fg="yellow", bg="green").pack()
root.mainloop()

##############################################################################
# example 5
counter = 0


def counter_label(label):
    def count():
        global counter
        counter += 1
        label.config(text=str(counter)[:-2] + '.' + str(counter)[-2:])
        label.after(10, count)
    count()


root = tk.Tk()
root.title("Counting Seconds")
label = tk.Label(root, fg="green")
label.pack()
counter_label(label)
button = tk.Button(root, text='Stop', width=25, command=root.destroy)
button.pack()
root.mainloop()
##############################################################################


# bupping
def printsup():
    print('sup')


root = tk.Tk()
text = "Fre sha va ca do"
label = tk.Label(root, text=text, bg="light blue")
label.pack()
button = tk.Button(root, text="waddup tho", command=printsup, width=50)
button.pack()
root.mainloop()


###################### MESSAGE WIDGET ###################################

master = tk.Tk()
quote = "There's nothing better than being American... this is the greatest feeling. If you don't love it, leave it. USA is Number 1!"
msg = tk.Message(master, text=quote)
msg.config(bg='lightgreen', font=('song ti', 24, 'italic'))
msg.pack()
tk.mainloop()


##################### BUTTON SECTION #################################
def write_slogan():
    print('Diggs! Sideline! Touchdown!')


root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
button = tk.Button(frame, text='QUIT', fg="red", command=root.destroy)
button.pack(side=tk.LEFT)

slogan = tk.Button(frame, text="oh yeah", command=write_slogan)
slogan.pack(side=tk.LEFT)

root.mainloop()


##################### RADIO BUTTONS ####################################
root = tk.Tk()
v = tk.IntVar()
label = tk.Label(root, text="Choose a bet type:", justify=tk.LEFT, padx=20)
label.pack()
tk.Radiobutton(root, text="Python", padx=20, variable=v, value=1).pack(anchor=tk.W)
tk.Radiobutton(root, text="Perl", padx=20, variable=v, value=2).pack(anchor=tk.W)
root.mainloop()


############## FILL OPTION ############################
root = tk.Tk()

w = tk.Label(root, text="Red Sun", bg="red", fg="white")
w.pack(fill=tk.X, ipady=10, side=tk.LEFT)
w = tk.Label(root, text="Green Grass", bg="green", fg="black")
w.pack(fill=tk.X, side=tk.LEFT)
w = tk.Label(root, text="Blue Sky", bg="blue", fg="white")
w.pack(fill=tk.X, side=tk.LEFT)

tk.mainloop()

######################### PLACE ###############################
root = tk.Tk()

root.geometry("700x500+2000+1100")

label = tk.Label(root, text='waddup tho... love it or leave it')
label.place(x=20, y=30, width=500, height=50)

root.mainloop()


########################## GRID ####################################
root = tk.Tk()

letters = list('aslkdfjs')

i = 0
for letter in letters:
    tk.Label(text=letter, relief=tk.RIDGE, width=15).grid(row=i, column=0)
    i += 1

root.mainloop()
