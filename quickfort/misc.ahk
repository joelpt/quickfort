;; Miscellaneous utility functions.

;; ---------------------------------------------------------------------------
;; Replace the file extension of the file in path with newExtension
ReplaceExtension(path, newExtension)
{
  SplitPath, path, , , , fileNoExt
  SplitPath, path, , dir
  result := dir . "\" . fileNoExt . newExtension
  return result
}
