  ; Demonstrated here:
  ; - comments
  ; - binary, hex, and decimal literals
  ; - named registers
  ; - jump to labels

  ldi 0b1 a     ; counter in register A
  LDI 0x2 B     ; limit in register B

loop:
  CMPJ B A end    ; continue looping while B >= A
  JMP end       ; escape loop if CMPJ failed
  INC A A       ; increment A
  JMP loop

end:
  HALT