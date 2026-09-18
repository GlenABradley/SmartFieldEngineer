"""Small real desktop command front end. No web server or inbound network listener."""
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog

FIELDS = {
 'observe-serial':['json'], 'assign-observation':['id','job','asset'],
 'observations':[], 'verify-bind':['observation','expected_revision','verifier','source','reason'],
 'recall-serial':['job','asset'], 'dispute-bind':['job','asset','expected_revision','reason'],
 'list': [], 'job':['json'], 'show':['job'], 'revise':['job','scope','source'],
 'record':['job','kind','json'], 'attach':['job','file','target','purpose','visibility'],
 'satisfy':['job','requirement','evidence','note'], 'track':['job','track','value','source'],
 'reserve':['job','arrival','review'], 'release':['job','reason'],
 'propose':['job','json','expires'], 'action':['id'], 'approve':['id','hash'],
 'outcome':['id','state','receipt'], 'receive':['sku','location','quantity','unit_price'],
 'consume':['job','sku','location','quantity'], 'document':['job','kind','json'],
 'economics':['job'], 'report':['job','html'], 'export':['job','zip'],
 'verify':[], 'backup':['destination']}

def main():
    root=tk.Tk();root.title('Network Engineer Copilot — Field Office proof of concept');root.geometry('1060x760')
    ttk.Label(root,text='Offline Field Office',font=('',22)).pack(anchor='w',padx=20,pady=10)
    ttk.Label(root,text='Local records and reviewed exports. External execution is manual. JSON examples are included in the kit.').pack(anchor='w',padx=20)
    home=tk.StringVar(value=os.environ.get('FIELD_OFFICE_HOME',str(Path.home()/'FieldOfficeData')))
    bar=ttk.Frame(root);bar.pack(fill='x',padx=20,pady=10)
    ttk.Label(bar,text='Data folder').pack(side='left');ttk.Entry(bar,textvariable=home,width=85).pack(side='left')
    choice=tk.StringVar(value='list');box=ttk.Combobox(root,textvariable=choice,values=list(FIELDS),state='readonly');box.pack(anchor='w',padx=20)
    form=ttk.Frame(root);form.pack(fill='x',padx=20,pady=10);entries={}
    output=tk.Text(root,wrap='word',font=('Courier',11));output.pack(fill='both',expand=True,padx=20,pady=10)
    def rebuild(*_):
        for child in form.winfo_children():child.destroy()
        entries.clear()
        for i,name in enumerate(FIELDS[choice.get()]):
            ttk.Label(form,text=name).grid(row=i,column=0,sticky='w')
            v=tk.StringVar(value='internal' if name=='visibility' else '')
            entries[name]=v;ttk.Entry(form,textvariable=v,width=95).grid(row=i,column=1,sticky='ew')
            if name in {'json','file'}:
                ttk.Button(form,text='Choose',command=lambda v=v:v.set(filedialog.askopenfilename())).grid(row=i,column=2)
        if choice.get()=='reserve':
            ttk.Label(form,text='Conservative defaults: work 240, inbound travel 60, closeout 30, recovery 90 minutes; soft hold. Use CLI for other values.').grid(row=99,column=0,columnspan=3)
    def run():
        args=[sys.executable,str(Path(__file__).with_name('fieldoffice.py')),'--home',home.get(),choice.get()]
        args.extend(entries[n].get() for n in FIELDS[choice.get()])
        result=subprocess.run(args,capture_output=True,text=True,timeout=60)
        output.delete('1.0','end');output.insert('end',result.stdout+result.stderr)
    ttk.Button(root,text='Run selected local operation',command=run).pack(anchor='w',padx=20,pady=8)
    box.bind('<<ComboboxSelected>>',rebuild);rebuild();root.mainloop()

if __name__=='__main__':main()
