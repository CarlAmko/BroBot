FROM golang:1.19.5
RUN apt-get update && apt-get install ffmpeg -y

WORKDIR /usr/src/app

COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .

RUN go build -v -o /usr/local/bin/app ./...

CMD ["app"]