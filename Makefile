

clean:
	$(shell find . -type f -regextype egrep -regex ".*\.(aux|log|fdb_latexmk|synctex\.gz|fls)" | xargs -d"\n" rm)
	
	@echo "Cleaned all intermediate LaTex files"
