var httpServer = require('http')
var url = require('url')
var qs = require('querystring')

httpServer.createServer(function(request, response){
	console.log(request.url)
	console.log(url)
	var a1 = url.parse(request.url).query
	console.log('a1:', typeof(a1), a1['name'])
	var a2 = url.parse(request.url, true).query
	console.log('a2:', typeof(a2), a2['name'])
	response.writeHead(200, {'Content-Type': "text/plain"})
	response.write('Hello')
	response.end('ok')
}).listen(8000)

