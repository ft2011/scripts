#! /usr/bin/env python3
# -*- coding: utf-8 -*-
######## ########################
##
##	F T <ft2011@gmail.com>
##	
##### #####################
######## ########################
##
##	main
##	
##### #####################
import sys
import os
import getopt
import re
import zlib
import re

replaceChar = {	ord('ä'): 'ae', ord('ö'): 'oe', ord('ü'): 'ue', 
				ord('á'): 'a',  ord('é'): 'e',  ord('ú'): 'u',
				ord('à'): 'a',  ord('è'): 'e',  ord('ù'): 'u',

				ord('Ä'): 'Ae', ord('Ö'): 'Oe', ord('Ü'): 'Ue',
				ord('À'): 'A',  ord('É'): 'E',  ord('Ú'): 'U',
				ord('À'): 'A',  ord('È'): 'E',  ord('Ù'): 'U',

				ord('['): "(",  ord(']'): ")",
				ord('ß'): "ss", ord(' '): "_",
				ord('&'): "and", ord('!'): "",
				ord('#'): "",  ord('*'): "", ord('\''): "", ord('\"'): ""}

includedRename = "."
includedChecksum = "."

excludedRename = "^\."
excludedChecksum = "[C|c]overs?|[P|p]roof|Sample|^\.|.*\.nfo$|.*\.jpg$|.*\.txt$|.*\.sfv$"

######## ########################
##
##	util
##	
##### #####################
def usage():
	print("scene_renamer.py [-v] [-r] [--no-sfv] [--no-rename] [-o output] -i /input/directory/")

######## ########################
##
##	rename
##
##	TODO: rename "inDir" itelf 
##	
##### #####################
def ren(inDir, verbose, recursive):	

	for f in os.listdir(inDir):
		if verbose:
			print("considering for rename: {}".format(f))

		# excluded?
		if re.match(excludedRename, str(f)):
			if verbose:
				print("excluded!")
			continue

		# included?
		if not re.match(includedRename, str(f)):
			if verbose:
				print("not included!")
			continue

		# recursive?
		if os.path.isdir(os.path.join(inDir, f)) and recursive:
			ren(os.path.join(inDir, f), verbose, recursive)

		# do renaming
		result = str(f)
		result = result.translate(replaceChar)
		result = re.sub(r"\s+", "_", result)
		result = re.sub(r"_+", "_", result)
		result = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", result)

		if str(f) == str(result):
			if verbose:
				print("nothing to rename...")
			continue

		if verbose:
			print("renaming in {}: '{}' to '{}'...".format(inDir, f, result))

		os.rename(os.path.join(inDir, f), os.path.join(inDir, result))

######## ########################
##
##	checksum
##	
##### #####################
def checksum(inDir, outFile, verbose, recursive):

	if os.path.isfile(os.path.join(inDir, outFile)):
		os.remove(os.path.join(inDir, outFile))

	if verbose:
		print("generating checksums in sfv-file: '{}'".format(outFile))

	for f in os.listdir(inDir):

		if verbose:
			print("considering for checksum: '{}'".format(f))

		# excluded?
		if re.match(excludedChecksum, str(f)):
			if verbose:
				print("excluded!")
			continue

		# included?
		if not re.match(includedChecksum, str(f)):
			if verbose:
				print("not included!")
			continue

		# recursive?
		if os.path.isdir(os.path.join(inDir, f)) and recursive:
			if verbose:
				print("is folder!")
			sfvFile = os.path.join(inDir, f, "{}.sfv".format(f))
			checksum(os.path.join(inDir, f), sfvFile, verbose, recursive)
			continue

		prev = 0
		for line in open(os.path.join(inDir, f), "rb"):
			prev = zlib.crc32(line, prev)

		crc32 = str("{0:08x}").format((prev & 0xFFFFFFFF))

		if verbose:
			print("done: {}...".format(crc32))

		with open(os.path.join(inDir, outFile), "a") as out:
			out.write("{} {}\n".format(str(f), crc32))

######## ########################
##
##	main (parsing, calling...)
##	
##### #####################
def main(argv=None):
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hrvo:i:sn", 
			["help", "recursive", "verbose", "output", "input", "no-sfv", "no-rename"])

	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err)) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	userIn = None
	userOut = None
	verbose = False
	doSfv = True
	doRename = True
	recursive = False

	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True

		elif o in ("-h", "--help"):
			usage()
			sys.exit()

		elif o in ("-i", "--input"):
			userIn = a

		elif o in ("-o", "--output"):
			userOut = a

		elif o in ("-s", "--no-sfv"):
			doSfv = False

		elif o in ("-n", "--no-rename"):
			doRename = False

		elif o in ("-r", "--recursive"):
			recursive = True
		else:
			assert False, "unhandled option"

	if verbose:
		print("input: {} output: {} verbose: {} sfv: {} rename: {} recursive: {}"
			.format(userIn, userOut, verbose, doSfv, doRename, recursive))

	## input is always needed
	if not userIn or not os.path.isdir(userIn):
		if verbose:
			print("no input-dir specified, check --help")
		sys.exit()

	######
	## rename
	####
	if doRename:
		ren(userIn, verbose, recursive)

	######
	## sfv
	####
	if doSfv:
		if not userOut or os.path.isdir(userOut):
			outFile = "{}.sfv".format(os.path.basename(os.path.abspath(userIn)))
		else:
			outFile = str(userOut)

		outFile = outFile.lower()
		checksum(userIn, outFile, verbose, recursive)

######## ########################
##
##	entry point
##	
##### #####################
if __name__ == "__main__":
    # ./scene_renamer.py -r -v -i /var/downloads/site/GAMES-PC/The.Sims.3.Seasons-RELOADED/
    sys.exit(main())
