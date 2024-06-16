def select_item(event):
    widget = event.widget
    index = int(widget.curselection()[0])
    value = widget.get(index)
    print("Ai selectat:", value)