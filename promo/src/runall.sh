cd "$(dirname "$0")"
run(){ for s in "$@"; do node cap.js $s 2.5 > logs_$s.txt 2>&1; echo "$s exit $? $(date +%T)"; done; }
run open sort ward isles &
run welcome dojo drink seasons pets &
wait
