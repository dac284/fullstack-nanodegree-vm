from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# imports for CRUD operations
from database_setup import Restaurant, Base, MenuItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Establish DB connection
engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body><h1>Restaurants</h1><br>"
                message += "<a href='/restaurants/new'>Make a new restaurant</a><br><br>"
                for restaurant in restaurants:
                    message += "<h2>"+restaurant.name+"</h2>"
                    message += "<a href='/restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    message += "<a href='/restaurants/%s/delete'>Delete</a><br>" % restaurant.id

                message += "</body></html>"
                self.wfile.write(message)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body>Enter a New Restaurant!"
                message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                message += "<h2>New Resaturant Entry Form</h2>"
                message += "<input name='restaurant' type='text' placeholder='New Restaurant Name'>"
                message += "<input type='submit' value='Create'> </form>"
                message += "</body></html>"
                self.wfile.write(message)
                return
            if self.path.endswith("/edit"):
                id_no = self.path.split('/')[-2]
                restaurant = session.query(Restaurant).filter_by(id=id_no).one()
                if restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    message = ""
                    message += "<html><body>Edit Restaurant %s" % restaurant.name
                    message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % id_no
                    message += "<h2>Edit Restaurant Name</h2>"
                    message += "<input name='restaurant' type='text' placeholder='%s'>" % restaurant.name
                    message += "<input type='submit' value='Rename'></form>"
                    message += "</body></html>"
                    self.wfile.write(message)
            if self.path.endswith("/delete"):
                id_no = self.path.split('/')[-2]
                restaurant = session.query(Restaurant).filter_by(id=id_no).one()
                if restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    message = ""
                    message += "<html><body>Confirm delete restaurant: %s" % restaurant.name
                    message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % id_no
                    message += "<input type='submit' value='Delete'></form>"
                    message += "</body></html>"
                    self.wfile.write(message)

	except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
	    	if ctype == 'multipart/form-data':
			fields = cgi.parse_multipart(self.rfile, pdict)
			name=fields.get('restaurant')[0]
	    	#Create new Restaurant Class
		newRestaurant = Restaurant(name = name)
	    	session.add(newRestaurant)
	    	session.commit()

		self.send_response(301)
		self.send_header('Content-type', 'text/html')
		self.send_header('Location','/restaurants')
		self.end_headers()
            if self.path.endswith('/edit'):
		print("got edit request")
		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
	    	if ctype == 'multipart/form-data':
		    fields = cgi.parse_multipart(self.rfile, pdict)
		name=fields.get('restaurant')
            	id_no = self.path.split('/')[-2]
	    	restaurant = session.query(Restaurant).filter_by(id=id_no).one()
		if restaurant:
		    restaurant.name = name[0]
		    session.add(restaurant)
		    session.commit()
		    self.send_response(301)
		    self.send_header('Content-type', 'text/html')
		    self.send_header('Location','/restaurants')
                    self.end_headers()
	    if self.path.endswith('/delete'):
		print("got delete request")
		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            	id_no = self.path.split('/')[-2]
	    	restaurant = session.query(Restaurant).filter_by(id=id_no).one()
		if restaurant:
		    session.delete(restaurant)
		    session.commit()
		    self.send_response(301)
		    self.send_header('Content-type', 'text/html')
		    self.send_header('Location','/restaurants')
		    self.end_headers()
        except:
	    print("post exception")
            pass
def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
