  ; Demonstrated here:
  ; - comments
  ; - binary, hex, and decimal literals
  ; - named registers
  ; - jump to labels

  LDI 1 A     ; counter in register A
  LDI 3 B     ; limit in register B
  
loop:
  CMPJ B A 2  ; continue looping while B >= A
  JMP end     ; escape loop if CMPJ failed
  INC A A     ; increment A
  JMP loop

end:
  HALT