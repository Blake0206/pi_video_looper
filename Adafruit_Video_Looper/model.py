# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import random
from os.path import basename
from typing import Optional, Union
from .video_looper import _print

random.seed()

class Movie:
    """Representation of a movie"""

    def __init__(self, target:str , title: Optional[str] = None, repeats: int = 1):
        """Create a playlist from the provided list of movies."""
        self.target = target
        self.filename = basename(target)
        self.title = title
        self.repeats = int(repeats)
        self.playcount = 0

    def was_played(self):
        if self.repeats > 1:
            # only count up if its necessary, to prevent memory exhaustion if player runs a long time
            self.playcount += 1
        else:
            self.playcount = 1

    def clear_playcount(self):
        self.playcount = 0
        
    def finish_playing(self):
        self.playcount = self.repeats+1
    
    def __lt__(self, other):
        return self.target < other.target

    def __eq__(self, other):
        if isinstance(other, str):
            return self.filename == other
        if isinstance(other, Movie):
            return self.target == other.target
        return False

    def __str__(self):
        return "{0} ({1})".format(self.filename, self.title) if self.title else self.filename

    def __repr__(self):
        return repr((self.target, self.filename, self.title, self.repeats, self.playcount))

class Playlist:
    """Representation of a playlist of movies."""

    def __init__(self, movies):
        """Create a playlist from the provided list of movies."""
        self._movies = movies
        self._index = None
        self._next = None

    def get_next(self, is_random, resume = False) -> Movie:
        """Get the next movie in the playlist. Will loop to start of playlist
        after reaching end.
        """
        # Check if no movies are in the playlist and return nothing.
        if len(self._movies) == 0:
            return None
        
        # Check if next movie is set and jump directly there:
        if self._next is not None:
            next=self._next
            self._next = None # reset next
            self._index=self._movies.index(next)
            return next
        
        # Start Random movie
        if is_random:
            self._index = random.randrange(0, self.length())
        else:
            # Start at the first movie or resume and increment through them in order.
            if self._index is None:
                if resume:
                    try:
                        with open('playlist_index.txt', 'r') as f:
                            self._index = int(f.read())
                    except FileNotFoundError:
                        self._index = 0
                else:
                    self._index = 0
            else:
                self._index += 1
                
            # Wrap around to the start after finishing.
            if self._index >= self.length():
                self._index = 0

        if resume:
            with open('playlist_index.txt','w') as f:
                f.write(str(self._index))

        return self._movies[self._index]
    
    # sets next by filename or Movie object or index
    def set_next(self, thing: Union[Movie, str, int]):
        _print('running set_next function')
        if isinstance(thing, Movie):
            _print('thing is a movie')
            if (thing in self._movies):
                self._next(thing)
        elif isinstance(thing, str):
            _print('thing is a string')
            """
            if _input == "baseball":
                _print('thing is baseball')
                 int = str(random.randrange(1, 6))
                 _print('baseball' + int + '.mp4')
                 self._next('baseball' + int + '.mp4')
            if _input == "basketball":
                 _print('thing is basketball')
                 int = str(random.randrange(1, 5))
                 _print('basketball' + int + '.mp4')
                 self._next('basketball' + int + '.mp4')
            if _input == "football":
                 _print('thing is football')
                 int = str(random.randrange(1, 3))
                 _print('football' + int + '.mp4')
                 self._next('football' + int + '.mp4')
            if _input == "boxing":
                 _print('thing is boxing')
                 int = str(random.randrange(1, 4))
                 _print('boxing' + int + '.mp4')
                 self._next('boxing' + int + '.mp4')
            if _input == "misc":
                 _print('thing is misc')
                 int = str(random.randrange(1, 2))
                 _print('misc' + int + '.mp4')
                 self._next('misc' + int + '.mp4')
            """
            if thing in self._movies:
                _print('thing is in movies...skipped custom function')
                self._next = self._movies[self._movies.index(thing)]
            elif thing[0:1] in ("+","-"):
                self._next = self._movies[(self._index+int(thing))%self.length()]
        elif isinstance(thing, int):
            _print('thing is an int...skipped custom function')
            if thing >= 0 and thing <= self.length():
                self._next = self._movies[thing]
        else:
            _print('thing is none')
            self._next = None
        self.clear_all_playcounts()
        self._movies[self._index].finish_playing() #set the current to max playcount so it will not get played again
       
    # sets next relative to current index
    def seek(self, amount:int):
        self.set_next((self._index+amount)%self.length())

    def length(self):
        """Return the number of movies in the playlist."""
        return len(self._movies)

    def clear_all_playcounts(self):
        for movie in self._movies:
            movie.clear_playcount()
