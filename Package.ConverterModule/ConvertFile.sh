#!/bin/bash

echo "INFO: Fase 1 - Extract all MKV files"
cd "/media/niklas/Niklas HardDrive/Series & Films"
#cd "/home/niklas/Videos"
touch log.txt
umask 677
allMKVFiles=$(find . -type f | grep -o -E ".*.mkv" ) 
IFS=$'\n'
#allMKVFiles=${allMKVFiles//' '/'\ '}
#allMKVFiles=${allMKVFiles//"'"/"\'"}
# Fase 1 : get all MKV files v1
echo "INFO: All MKV files: $allMKVFiles"

# Fase 2 : Foreach iterate
echo "INFO: Fase 2 - Videos"
for currentVideo in ${allMKVFiles[@]}; do
    echo "INOF: The current Video is: $(echo "$currentVideo")"
    allSubtitles=($(ffprobe -loglevel error -select_streams s -show_entries stream=index:stream_tags=language -of csv=p=0 $(echo $currentVideo)))
    amountOfSubtitles=${#allSubtitles[@]}
    #Fase 3 : Converting all of the subtitles files to their output
    echo "INFO: Fase - Subtitles 3" #amountOfSubtitles

    filenameBase=$(echo $currentVideo | sed 's/\.mkv$//')
    echo "INFO: The base for the filename is : $filenameBase"

    for ((i=0;i<amountOfSubtitles;i++)); do
        currentSubtitle=${allSubtitles[i]}
        echo "INFO: The current Subtitle is: $currentSubtitle"
        language=$(echo $currentSubtitle | grep -o -E "[a-z]*")
        echo "INFO: The extracted string for this subtitle is: $language"


        #echo "$filenameBase"
        filenameCompositeVTT=$(echo "${filenameBase}_${language}.vtt")
        filenameCompositeSRT=$(echo "${filenameBase}_${language}.srt")
        echo "INFO: The filenames will be : $filenameCompositeVTT and $filenameCompositeSRT"

        ffmpeg -hide_banner -loglevel error -i $currentVideo -map 0:s:$i? -y $(echo $filenameCompositeSRT)
        ffmpeg -hide_banner -loglevel error -i $currentVideo -map 0:s:$i? -y $(echo $filenameCompositeVTT)

        exitCode=$(echo $?)
        # Check if the output contains 'error' (case insensitive)
        if [ $exitCode -eq 0 ]; then
            canDelete=1
        else
            canDelete=0
        fi

        chmod 644 $(echo $filenameCompositeSRT)
        chmod 644 $(echo $filenameCompositeVTT)


        echo "INFO: Subs made successfully!"
        
    #    subtitleName = 
    #    ffmpeg -i $currentVideo -map 0:s:0 subs.srt
    done

    echo "Now Creating the MP4 file instead"

    ffmpeg -hide_banner -loglevel error -i $currentVideo -codec copy -y $(echo "$filenameBase.mp4")
    #ffmpeg -i $currentVideo -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k $(echo "$filenameBase.mp4")

    exitCode=$(echo $?)
    # Check if the output contains 'error' (case insensitive)
    if [ $exitCode -eq 0 ]; then
        canDelete=$((canDelete*1))
    else
        ffmpeg -i $currentVideo -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k $(echo "$filenameBase.mp4")
        canDelete=0
    fi


    chmod 644 $(echo $filenameBase.mp4)

    fileFoundQV=$(find . -type f | grep -o -E ".*$basename.*.mp4")
    fileFoundQS=$(find . -type f | grep -o -E ".*$basename.*.vtt")

    if [ -n "$fileFoundQV" ] && [ -n "$fileFoundQS" ]; then
        canDelete=$((canDelete*1))
        echo "Both MP4 and VTT files found. Can delete: $canDelete"
    else
        canDelete=0
        echo "Missing either MP4 or VTT file. Can delete: $canDelete"
    fi


    if (($canDelete==1)); then
        echo "Sufficient evidence found that the file has successfully been converted, deleting .mkv file"
        rm $currentVideo
    else
        echo "Something went wrong with move $currentVideo" >> log.txt
    fi

done

IFS=$' \t\n'