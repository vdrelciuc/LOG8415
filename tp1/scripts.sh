docker build -t log8415-aws-tp1 .
docker run --volume "$(pwd)/graphs:/graphs" log8415-aws-tp1
