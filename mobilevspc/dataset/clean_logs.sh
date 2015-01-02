set -o verbose

gzcat -f $(ls -1 apache-logs/access* | sort -t . -k 3 -n | gtac) | grep -E 'userevent|accountsjson\/register' | grep -Ev 'disaster|quake|v24-es' | grep -v ' 301 ' > apache.log

# CUTOFF=$(fgrep -n '[08/Sep/2014:13:33:07 -0700]' apache-clean.tmp | cut -d : -f1)
# head -$(( $CUTOFF - 1 )) apache-clean.tmp > apache-v1.log
# tail +$CUTOFF apache-clean.tmp > apache-v2.log
# rm apache-clean.tmp
