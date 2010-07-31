/*
    ; if we're doing repeats (Alt+R) we handle it here. output is repeated and chained together with necessary movement commands
    ; to get to the correct next tile for each successive output.
    if (RepeatPattern) {
      moves := ""

      ; targetZLevel is the level, relative to the level we started the initial block on, that we want to be on in order to begin the
      ; next block. zLevel currently contains the level we actually are on now, again relative to the initial block (0 = same level,
      ; 1 = one level above)
      if (RepeatDir = "d" || RepeatDir = "u") {
        ; next placement needs to occur on the z-level above or below the initial one. adjust targetZLevel accordingly.
        ; To accommodate for multilevel blueprints, we multiply this z-level shift by the number of floors in the blueprint.
        targetZLevel := (RepeatDir = "u" ? 1 : -1) * (1 + Abs(zLevel))
      }
      else {
        ; repeating in a cardinal direction - we need to start back on the same level we built the last block on every time
        targetZLevel := 0
      }

      ; Now make targetZLevel relative to our CURRENT level, by subtracting our current level from it.
      targetZLevel -= zLevel

      ; Finally we can issue any moves needed to get onto the correct relative z-level
      if (targetZLevel < 0) {
        moves := moves . RepeatStr(">", -targetZLevel)
      }
      else if (targetZLevel > 0) {
        moves := moves . RepeatStr("<", targetZLevel)
      }

      ; Then move one of the four cardinal directions (exactly one 'block' away, touching the current block) or down/up (directly above or below)
      ;if (RepeatDir = "u")
      ;  moves := moves . "<"
      ;else if (RepeatDir = "d")
      ;  moves := moves . ">"
      ;else
      if (RepeatDir = "n")
        moves := moves . RepeatStr("{U}", height)
      else if (RepeatDir = "s")
        moves := moves . RepeatStr("{D}", height)
      else if (RepeatDir = "e")
        moves := moves . RepeatStr("{R}", width)
      else if (RepeatDir = "w")
        moves := moves . RepeatStr("{L}", width)

      ; If CSV has a start() specification, adjust for this
      if (StartPosAbsX > 0) {
        moves := moves . GetCursorMoves(StartPosAbsX - 1, StartPosAbsY - 1, 0)
      }

      output := RepeatStr(output . moves, RepeatCount - 1) . output


      RepeatCount := 0
      RepeatDir := ""
    }
*/
