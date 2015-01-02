mysql -e "DELETE FROM cafe_demo1.log_user_events WHERE created < '2014-01-11'; UPDATE crc_spanish.log_user_events SET logger_id=589 WHERE logger_id BETWEEN 590 AND 602"
