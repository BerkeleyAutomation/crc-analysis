login="$(USER)@californiareportcard.org"

start_mysql:
	mysql.server status || mysql.server start

get_logs:
	mkdir -p apache-logs
	rsync -a --progress $(login):/var/log/apache2/access* apache-logs/.

get_sql_dump:
	ssh $(login) "mysqldump -u root -p crc_spanish" > crc_spanish.sql

load_sql_dump: start_mysql
	mysql -e "drop database if exists crc_spanish; create database crc_spanish"
	mysql crc_spanish < crc_spanish.sql

clean_logs:
	bash clean_logs.sh

gen_dataset:
	python gen_dataset.py cafe_demo1 &
	python gen_dataset.py crc_spanish &

