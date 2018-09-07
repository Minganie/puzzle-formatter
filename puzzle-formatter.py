import argparse
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import numpy as np
import cv2
from fpdf import FPDF
import tempfile
import os
import calendar
import random


def get_from_the_net(n, game, size):
    games = []
    for i in range(n):
        try:
            driver = webdriver.Firefox()
            wait = WebDriverWait(driver, 5)
            driver.get("https://www.puzzle-" + game + ".com/?size=" + str(size))
            wait.until(
                EC.presence_of_element_located((By.ID, "puzzleContainer"))
            )
            script = """window.stop();
                      var el = document.getElementById('puzzleContainer');
                      var rect = el.getBoundingClientRect(),
                      scrollLeft = window.pageXOffset || document.documentElement.scrollLeft,
                      scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                      var so = { top: rect.top + scrollTop, left: rect.left + scrollLeft };
                      window.scrollTo(so.left, so.top);"""
            driver.execute_script(script)
            time.sleep(0.1)
            pic = pyautogui.screenshot()
            repic = np.array(pic)
            img = cv2.cvtColor(repic, cv2.COLOR_RGB2BGR)
            # cv2.imshow('Whole capture', img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            games.append(find_nurikabe(img))
            # cv2.imshow('One nurikabe', games[i])
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        finally:
            driver.quit()
    return games


def get_ks_from_the_net(n):
    games = []
    for i in range(n):
        try:
            driver = webdriver.Firefox()
            wait = WebDriverWait(driver, 5)
            random_month = random.choice(range(1, 12, 1))
            random_day = (random.choice([date for date in calendar.Calendar().itermonthdates(2018, random_month)
                                         if date.month == random_month])).day
            # print "Found date m: %02d, d: %02d" % (random_month, random_day)
            url = "http://www.brainbashers.com/showkillersudoku.asp?date=%02d%02d&diff=4" % (random_month, random_day)
            # print "Going to look at '%s'" % url
            driver.get(url)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.sudokutable"))
            )
            driver.find_element_by_id("showwrong").send_keys(Keys.NULL)     # Focus random checkbox to avoid seeing
            time.sleep(0.1)                                                 # the cursor in the sudoku table
            pic = pyautogui.screenshot()
            repic = np.array(pic)
            img = cv2.cvtColor(repic, cv2.COLOR_RGB2BGR)
            # cv2.imshow('Whole capture', img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            games.append(find_ksudoku(img))
            # cv2.imshow('One nurikabe', games[i])
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        finally:
            driver.quit()
    return games


def get_from_the_disk(n, game, size):
    games = []
    for i in range(n):
        path = "path\\%s%d.png" % (game, i)
        img = cv2.imread(path)
        games.append(img)
    return games


def is_big(contour):
    peri = cv2.arcLength(contour, True)
    return peri > 900


def is_square(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
    if len(approx) != 4:
        return False
    else:
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)
        return 0.95 < ar < 1.05


def find_nurikabe(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 181, 194])
    upper_blue = np.array([120, 201, 214])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    masked = cv2.bitwise_and(hsv, hsv, mask=mask)
    blurred = cv2.GaussianBlur(masked, (5, 5), 0)
    gray = cv2.cvtColor(cv2.cvtColor(blurred, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    squares = [contours[i] for i in range(len(contours)) if is_square(contours[i]) and is_big(contours[i])]
    squares = squares[0]
    squares = [squares[0][0], squares[1][0], squares[2][0], squares[3][0]]
    top = min(squares[0][0], squares[1][0], squares[2][0], squares[3][0])
    bottom = max(squares[0][0], squares[1][0], squares[2][0], squares[3][0])
    left = min(squares[0][1], squares[1][1], squares[2][1], squares[3][1])
    right = max(squares[0][1], squares[1][1], squares[2][1], squares[3][1])
    # print left, right, top, bottom
    roi = img[left + 1:right, top + 1:bottom]
    return roi


def find_ksudoku(img):
    # cv2.imwrite('D:\megha\Documents\whole_capture.png', img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, masked = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
    blurred = cv2.GaussianBlur(masked, (5, 5), 0)
    # cv2.imshow('Masked', masked)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    im2, contours, hierarchy = cv2.findContours(blurred, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    squares = [contours[i] for i in range(len(contours)) if is_square(contours[i]) and is_big(contours[i])]
    # print len(squares)
    # cv2.drawContours(img, squares, -1, (255, 255, 0), 3)
    # cv2.imshow('thingies', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    squares = squares[0]
    squares = [squares[0][0], squares[1][0], squares[2][0], squares[3][0]]
    top = min(squares[0][0], squares[1][0], squares[2][0], squares[3][0])
    bottom = max(squares[0][0], squares[1][0], squares[2][0], squares[3][0])
    left = min(squares[0][1], squares[1][1], squares[2][1], squares[3][1])
    right = max(squares[0][1], squares[1][1], squares[2][1], squares[3][1])
    # print left, right, top, bottom
    roi = cv2.bitwise_not(masked)[left:right, top:bottom]
    return roi


def pad_equalize(im_list):
    height = max([im.shape[0] for im in im_list])
    width = max([im.shape[1] for im in im_list])
    # print "Making all images %d x %d" % (width, height)
    im_list2 = [cv2.copyMakeBorder(im, 0, height-im.shape[0], 0, width-im.shape[1], cv2.BORDER_CONSTANT,
                                   value=[255, 255, 255]) for im in im_list]
    return im_list2


def make_two_by_page(games):
    assert len(games) == 2
    gois = pad_equalize(games)
    return cv2.vconcat((gois[0], gois[1]))


def make_four_by_page(games):
    assert len(games) == 4
    gois = pad_equalize(games)
    row0 = cv2.hconcat((gois[0], gois[1]))
    row1 = cv2.hconcat((gois[1], gois[2]))
    return cv2.vconcat((row0, row1))


def make_six_by_page(games):
    assert len(games) == 6
    gois = pad_equalize(games)
    row0 = cv2.hconcat((gois[0], gois[1]))
    row1 = cv2.hconcat((gois[1], gois[2]))
    row2 = cv2.hconcat((gois[3], gois[4]))
    return cv2.vconcat((row0, row1, row2))


def make_full_pdf(pages):
    pdf = FPDF('P', 'in', 'Letter')
    for page in pages:
        pdf.add_page()
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        f.close()  # file is not immediately deleted because we used delete=False
        cv2.imwrite(f.name, page)
        pdf.image(f.name, x=0.5, y=0.5, w=7.5, h=10, type='PNG', link='')
        os.unlink(f.name)
    return pdf


def make_width_pdf(pages):
    pdf = FPDF('P', 'in', 'Letter')
    for page in pages:
        pdf.add_page()
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        f.close()  # file is not immediately deleted because we used delete=False
        cv2.imwrite(f.name, page)
        pdf.image(f.name, x=0.5, y=0.5, w=7.5, type='PNG', link='')
        os.unlink(f.name)
    return pdf


def main():
    parser = argparse.ArgumentParser(description='Create a printable pdf of paper games.')
    parser.add_argument('pages', metavar='n', type=int, help='number of pages desired')
    parser.add_argument('--game', dest='game',
                        help="game desired, choices are 'ksudoku', 'nurikabe', 'dominosa', 'loop'")
    parser.add_argument('--output', dest='output', help="Path and filename for pdf output")

    args = parser.parse_args()
    npages = args.pages
    game = args.game
    output = args.output
    print "Preparing %d page(s) of %s games" % (npages, game)
    if game == 'ksudoku':
        ngames = npages * 2
        games = get_ks_from_the_net(ngames)
        if len(games) != ngames:
            raise RuntimeError("Couldn't find %d %s games" % (ngames, game))
        else:
            pages = []
            for i in range(npages):
                page = make_two_by_page(games[2 * i:2 * i + 2])
                pages.append(page)
            pdf = make_full_pdf(pages)
            pdf.output(output, 'F')
    elif game == 'nurikabe':
        ngames = npages * 4
        games = get_from_the_net(ngames, 'nurikabe', 4)
        # games = get_from_the_disk(ngames, 'nurikabe', 4)
        if len(games) != ngames:
            raise RuntimeError("Couldn't find %d %s games" % (ngames, game))
        else:
            pages = []
            for i in range(npages):
                page = make_four_by_page(games[4 * i:4 * i + 4])
                pages.append(page)
            pdf = make_width_pdf(pages)
            pdf.output(output, 'F')
    elif game == 'dominosa':
        ngames = npages * 6
        games = get_from_the_net(ngames, 'dominosa', 2)
        if len(games) != ngames:
            raise RuntimeError("Couldn't find %d %s games" % (ngames, game))
        else:
            pages = []
            for i in range(npages):
                page = make_six_by_page(games[6 * i:6 * i + 6])
                pages.append(page)
            pdf = make_full_pdf(pages)
            pdf.output(output, 'F')
    elif game == 'loop':
        ngames = npages * 1
        games = get_from_the_net(ngames, 'loop', 9)
        if len(games) != ngames:
            raise RuntimeError("Couldn't find %d %s games" % (ngames, game))
        else:
            pages = []
            for i in range(npages):
                page = games[i]
                pages.append(page)
            pdf = make_full_pdf(pages)
            pdf.output(output, 'F')
    else:
        raise TypeError("Unknown game '%s', choices are 'ksudoku', 'nurikabe', 'dominosa', 'loop'" % game)


if __name__ == "__main__":
    main()
