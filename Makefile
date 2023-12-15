build:
	hugo --minify --gc --cleanDestinationDir

server:
	hugo server

# Doens't work yet
games:
	cd external/lung-pong/ && vite build --outDir ../../content/games/lung-pong/ --base /games/01-lung-pong/
