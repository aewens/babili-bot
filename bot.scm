(use tcp irregex ports srfi-13 srfi-14 srfi-69)

(define bot-nick "BabiliBot|scm")

(define (send out message)
    (format out (string-append message "\r\n")))

(let-values
    ([(in out)
        (tcp-connect "127.0.0.1" 6667)])
    (send out 
        (string-append 
            "USER "
            (string-join (vector->list (make-vector 4 bot-nick)) " ")))
    (send out (string-append "NICK " bot-nick))
    (let loop
        ([line (read-line in)])
        (if (eof-object? line)
        line
        (begin
            (print line)
            (loop (read-line in))))))