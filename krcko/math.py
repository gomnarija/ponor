import math
from typing import Tuple

#math stuff :)


class point:
	def __init__(self,y :int, x :int):
		self.y = y
		self.x = x

	def distance(self, p :'point') -> int:
		return 	int(math.sqrt(math.pow(p.x-self.x,2)+math.pow(p.y-self.y,2)))

class rectangle:
	def __init__(self,height :int, width :int, y :int ,x :int):
		self.height = height
		self.width  = width
		self.y	    = y
		self.x      = x

	@property
	def top(self) -> int:
		return self.y
	@property
	def bottom(self) -> int:
		return self.y + self.height
	@property
	def left(self) -> int:
		return self.x
	@property
	def right(self) -> int:
		return self.x + self.width
	@property
	def tl(self) -> point:
		return point(self.y,self.x)
	@property
	def tr(self) -> point:
		return point(self.y,self.x+self.width)
	@property
	def bl(self) -> point:
		return point(self.y+self.height,self.x)
	@property
	def br(self) -> point:
		return point(self.y+self.height,self.x+self.width)
	
	@property
	def area(self) -> int:
		return self.width * self.height

	def contains_point(self, p :point) -> bool:
		return p.y >= self.top and p.y <= self.bottom\
			and p.x >= self.left and p.x <= self.right

	
	def overlap(self, rect :'rectangle') -> Tuple[bool, 'rectangle']:
		
		overlap_rect :rectangle = rectangle(0,0,0,0)

		overlap_rect.height = max(0, min(self.bottom, rect.bottom) - max(self.top, rect.top))
		overlap_rect.width  = max(0, min(self.right, rect.right) - max(self.left, rect.left))


		overlap_rect.y = max(rect.top, self.top)
		overlap_rect.x = max(rect.left, self.left)


		they_overlap :bool = True if overlap_rect.height > 0 and overlap_rect.width > 0 else False

		return (they_overlap, overlap_rect)

