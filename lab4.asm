  ; Demonstrated here:
  ; - comments
  ; - binary, hex, and decimal literals
  ; - named registers
  ; - jump to labels
  ; Unfortunately negative jumps are not possible because
  ; RD is only 4 bits wide, but PC is 8 bits, so we can't overflow it.
  ; So our machine doesn't support loops :(

  LDI  0b1  A    ; put 1 into count register A
  LDI  0x04 B    ; put 4 into limit register B

  ADI   A 3 A    ; Add to counter
  CMPJ  B A end  ; skip the next instruction if B >= A
  NOP
end:
  HALT