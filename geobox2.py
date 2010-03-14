"""
Copyright (c) 2010, Patrick Hughes
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of "Fluffy Bunny Software" nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
This is a re-implementation of the geobox concept provided by
bslatkin@gmail.com (Brett Slatkin) in the geobox.py project.

Description:
http://code.google.com/appengine/articles/geosearch.html
Original Code:
http://code.google.com/p/google-app-engine-samples/source/browse/#svn/trunk/24hrsinsf

The goal here is to provide a simplified interface for geobox
searching. This version is implemented as a class which you 
initialize with coordinates, and request a list of geobox strings
for storage in the db. 

To search for stored objects we initialize with coordinates
and a scope, request a box to search on. The box is returned
as a string. This string is passed to the query.

pat@phughes.us (Patrick Hughes)
"""

import decimal
import logging

SCOPE_SIZES = [decimal.Decimal('0.00625'), decimal.Decimal('0.0125'), decimal.Decimal('0.025'), decimal.Decimal('0.05')]
NUM_PLACES = decimal.Decimal('1.000') # use 3 decimal places
MARGIN = decimal.Decimal('0.3')

class Geobox:
	latitude = decimal.Decimal()
	longitude = decimal.Decimal()
	
	def __init__(self, latitude, longitude):
		self.latitude = decimal.Decimal(str(latitude))
		self.longitude = decimal.Decimal(str(longitude))	
		

	def storage_geoboxes(self):
		# returns the string-list of geoboxes to store in the database
		list = []
		
		# get the search geoboxes for each scope in SCOPE_SIZES
		for scope in SCOPE_SIZES:
			list.append(self.bounding_box(self.latitude, self.longitude, scope))
					
			# if we're close to the edge add the adjacent bounding box
			if self.extend_right(scope):
				list.append(self.bounding_box(self.latitude, self.longitude + scope, scope))
			
			if self.extend_down(scope):
				list.append(self.bounding_box(self.latitude - scope, self.longitude, scope))
				
			if self.extend_left(scope):
				list.append(self.bounding_box(self.latitude, self.longitude - scope, scope))
				
			if self.extend_up(scope):
				list.append(self.bounding_box(self.latitude + scope, self.longitude, scope))
				
			# same thing in the corner 
			if self.extend_right(scope) and self.extend_down(scope):
				list.append(self.bounding_box(self.latitude - scope, self.longitude + scope, scope))
				
			if self.extend_left(scope) and self.extend_up(scope):
				list.append(self.bounding_box(self.latitude + scope, self.longitude - scope, scope))
			
		#logging.info(list)
		return [self.string_for_bounding_box(box) for box in list]
		
		
	def search_geoboxes(self, scope):
		# Returns a geobox to pass to a Query object.
		# Generally this should be the smallest box that 
		# encompasses scope.
		scope = self.nearest_scope(scope)
		
		#logging.info('creating geopboxes for scope: ' + str(scope))
		#logging.info('latitude: ' + str(self.latitude) + ' longitude: ' + str(self.longitude))
				
		box = self.bounding_box(self.latitude, self.longitude, scope))

		# convert the tupples in into a string
		return self.string_for_bounding_box(box)
		
	# calculates a bounding box
	def bounding_box(self, lat, lon, scope):
		adjusted_top = self.round_down(lat, scope) + scope
		adjusted_right = self.round_down(lon, scope) + scope
		adjusted_bottom = self.round_down(lat, scope)
		adjusted_left = self.round_down(lon, scope)

		return (adjusted_top, adjusted_left, adjusted_bottom, adjusted_right)
		
	def string_for_bounding_box(self, box):
		return "|".join(str(s.quantize(NUM_PLACES)) for s in box)
		
	def nearest_scope(self, scope):
		scope = decimal.Decimal(str(scope)).quantize(NUM_PLACES, rounding= decimal.ROUND_HALF_UP)
		adjusted_scope = None
		# keep scope within the bounds
		if scope >= SCOPE_SIZES[-1]:
			adjusted_scope = SCOPE_SIZES[-1]
 		else:
			for s in reversed(SCOPE_SIZES):
				if scope < s:
					adjusted_scope = s
		
		return adjusted_scope
	
	def extend_right(self, scope):
		r = self.round_down(self.longitude, scope)
		if abs(self.longitude - r) < scope * MARGIN:
			return True
		return False
		
	def extend_down(self, scope):
		b = self.round_down(self.latitude, scope)
		if abs(self.latitude - b) < scope * MARGIN:
			return True
		return False

	def extend_left(self, scope):
		l = self.round_down(self.longitude, scope) + scope
		if abs(l - self.longitude) < scope * MARGIN:
			return True
		return False

	def extend_up(self, scope):
		t = self.round_down(self.latitude, scope) + scope
		if abs(t - self.latitude) < scope * MARGIN:
			return True
		return False

	def round_down(self, coord, scope):
		try:
			remainder = coord % scope
			if coord > 0:
				return coord - remainder
			else:
				return coord - remainder - scope
		except decimal.InvalidOperation:
			#logging.info('returning coordinate untouched')
			# This happens when the scope is too small for the current coordinate.
			# That means we've already got zeros in the scope's position, so we're
			# already rounded down as far as we can go.
			return coord

	
def test():
	print("testing geobox.py")
	lat = "43.16956"
	lon = "-77.61139"
	print("init with coordinates: " + lat + " & " + lon)
	gb = Geobox(lat, lon)
	test_gb(gb)
	lat = "-43.16956"
	lon = "77.61139"
	print("init with coordinates: " + lat + " & " + lon)
	gb = Geobox(lat, lon)
	test_gb(gb)
	print("\n\nTests finished")
	
	
def test_gb(gb):
	for scope in SCOPE_SIZES:
		print("\n\nSetting scope size: " + str(scope))
		print("\n-------testing latitude expansion:------------")
		print("margin size: " + str(scope * MARGIN))
		print("rounded: " + str(gb.round_down(gb.latitude, scope)) + " less than lat: " + str(gb.latitude) + " ?")
		
		print(str(abs(gb.round_down(gb.latitude, scope) + scope - gb.latitude)) + " < " + str(scope * MARGIN))
		print("extend_up: " + str(gb.extend_up(scope)))
		print(str(abs(gb.latitude - gb.round_down(gb.latitude, scope))) + " < " + str(scope * MARGIN))
		print("extend_down: " + str(gb.extend_down(scope)))
		
		print("\n-------testing longitude expansion:------------")
		print("margin size: " + str(scope * MARGIN))
		print("rounded: " + str(gb.round_down(gb.longitude, scope)) + " less than lat: " + str(gb.longitude) + " ?")
		
		print(str(abs(gb.round_down(gb.longitude, scope) - gb.longitude)) + " < " + str(scope * MARGIN))
		print("extend_right: " + str(gb.extend_right(scope)))
		print(str(abs(gb.round_down(gb.longitude, scope) + scope - gb.longitude)) + " < " + str(scope * MARGIN))
		print("extend_left: " + str(gb.extend_left(scope)))

		
	
if __name__ == "__main__":
  test()
	
	
	