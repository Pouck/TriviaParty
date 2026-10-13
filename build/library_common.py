"""Concise authoring helpers for the balanced library expansion."""
def mc(prompt,answer,distractors,image=None):
 return dict(prompt=prompt,options=[answer,*distractors],index=0,image=image)
def buzz(prompt,answer,image=None,aliases=()):
 return dict(prompt=prompt,answers=[answer,*aliases],image=image)
def who(answer,clues,aliases=()):
 assert len(clues)==4
 return dict(answers=[answer,*aliases],clues=clues)
def timeline(prompt,events,sources=()):
 return dict(prompt=prompt,events=events,sources=list(sources))
def topic(slug,title,subject,sources,choices,buzzers,guesses,chronologies=()):
 assert len(choices)==len(buzzers)==len(guesses)==5
 assert not chronologies or len(chronologies)==5
 return dict(slug=slug,title=title,subject=subject,sources=sources,
   qcm=choices,buzzer=buzzers,qsj=guesses,chronologie=list(chronologies))
