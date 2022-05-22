import sys

import deepl_manager as deepl_manager
import sub_translator as sub_translator
import ass_parser as ass_parser
import os
import file_utils as file_utils
import time

DEBUG_SUBS = 0

def main(args):
    print("main")
    # deepl_manager.open_browser()

    # srt_array = srt_parser.from_srt("H:/Media/Animes/GrandBlueWeb/[HorribleSubs] Grand Blue - 02 [1080p].srt")
    # srt_text = srt_parser.to_srt(srt_array)
    #
    # print(srt_array)
    # print(srt_text)

    # file_utils.readtxt_encoded('H:/Media/Animes/GrandBlueWeb/[HorribleSubs] Grand Blue - 02 [1080p]_pt_BR.srt')

    # path = 'E:/Media/Animes/Ano Hi mita/[n3-PLAF] Ano Hana - O Filme [BDRip][720p]/'
    path = 'E:/Media/Animes/The Daily Life Of The Immortal King s02/The Daily Life of the Immortal King - Season 2/'
    files = file_utils.list_files(path, [".srt", ".ass"], ["pt_BR"], ["en"])
    start_file = 8
    files_props = [
        {
            "pos": 8,
            "start": 8,
            "end": 0
        }
    ]

    print(files)

    driver = None

    if (DEBUG_SUBS == 0):
        # Open broser translator
        driver = deepl_manager.open_browser()
        deepl_manager.changeLanguages(driver, "EN")
        # print(deepl_manager.translate(driver, "I need water"))


    for i in range(start_file, len(files)):
        file_at = files[i]
        file_at_start_pos = 0
        file_at_end_pos = 0
        for x in range(0, len(files_props)):
            file_prop_at = files_props[x]
            file_prop_at_pos = file_prop_at["pos"]
            file_prop_at_start = file_prop_at["start"]
            file_prop_at_end = file_prop_at["end"]

            if file_prop_at_pos == i:
                file_at_start_pos = file_prop_at_start
                file_at_end_pos = file_prop_at_end
                print("break")
                break

        print("file at:", file_at)

        if (DEBUG_SUBS == 0):
            sub_translator.translate(file_at, file_at_start_pos, file_at_end_pos, driver=driver)
        else:
            sub_translator.translate(file_at, file_at_start_pos, file_at_end_pos)

    # time.sleep(1000)



if __name__ == "__main__":
    main(sys.argv)