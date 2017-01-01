package autoVocabulary

import (
	"bufio"
	"fmt"
	"log"
	"os"
)

var (
	HisFilePath     string     = fmt.Sprintf("%s", "/Users/leowu/.goldendict/history")
	DisFilePath     string     = fmt.Sprintf("%s", "/Users/leowu/Documents/wordList")
	DictionaryPath  string     = fmt.Sprintf("%s", "./automate/autoVocabulary/dictionary")
	DictionaryWords *WordsList = new(WordsList)
)

const (
	WORDFLAG int = 0 //This flag is just used for saving words in map
)

type WordsList struct {
	words map[string]int
}

func init() {
	DictionaryWords.words = make(map[string]int)
	DictionaryWords = generateWordsList(DictionaryPath)
}

func AutomateUpdateVocabularyList() {
	updateProcedure()
}

func updateProcedure() {
	allWordsOldList := generateWordsList(DisFilePath)
	originalWordsNum := len(allWordsOldList.words)
	historyWordsList := generateWordsList(HisFilePath)
	allWordsNewList := generateAllNewWordsList(historyWordsList, allWordsOldList)
	if len(allWordsNewList.words) <= originalWordsNum {
		return //It is not necessary to rewrite vocabulary file if no pure new words yield by goldendict.
	}
	writeWordsToFile(allWordsNewList)
}

func generateWordsList(filePath string) *WordsList {
	//check whether the file exist, if not create it.
	if _, err := os.Stat(filePath); err != nil {
		_, err = os.Create(DisFilePath)
		if err != nil {
			log.Fatal(err)
		}
	}
	disFile, _ := os.OpenFile(filePath, os.O_RDWR|os.O_APPEND, 0660)
	defer disFile.Close()
	wordList := scannerWords(disFile)
	return wordList
}

func scannerWords(file *os.File) *WordsList {
	wordsList := new(WordsList)
	wordsList.words = make(map[string]int)

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanWords)
	for scanner.Scan() {
		if isNumber(scanner.Text()) {
			continue
		}
		wordsList.words[scanner.Text()] = WORDFLAG
	}
	return wordsList
}

func generateAllNewWordsList(historyWords *WordsList, allWords *WordsList) *WordsList {
	for wordInHistory, _ := range historyWords.words {
		allWords.words[wordInHistory] = WORDFLAG
	}
	return allWords
}

func writeWordsToFile(words *WordsList) {
	getRidWrongWords(words)
	if len(words.words) == 0 {
		return
	}
	disFile, _ := os.OpenFile(DisFilePath, os.O_RDWR, 0660)
	defer disFile.Close()

	disbuf := bufio.NewWriter(disFile)

	num := 0
	nextPosition := 0
	for word, _ := range words.words {
		disbuf.write_string(word)
		blankLength := 20 - len(word)
		if blankLength <= 0 {
			blankLength = 5
			nextPosition += len(word) + 5
		} else {
			nextPosition += 20
		}
		for i := 0; i < blankLength; i++ {
			disbuf.write_string(" ")
		}

		num++
		if num%8 == 0 {
			disbuf.write_string("\r\n")
			nextPosition = 0
		}
		if err := disbuf.Flush(); err != nil {
			panic(err)
		}
	}
}

func isNumber(str string) bool {
	for i := 0; i < len(str); i++ {
		if 48 <= int(str[i]) && int(str[i]) <= 57 {
			return true
		}
	}
	return false
}

func getRidWrongWords(wordsList *WordsList) {
	for word, _ := range wordsList.words {
		if _, ok := DictionaryWords.words[word]; !ok {
			delete(wordsList.words, word)
		}
	}
}

func checkError(err error) {
	if err != nil {
		fmt.Println(err.Error())
		os.Exit(0)
	}
}
