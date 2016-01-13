/* main.c - requester demo application

   This file is part of amiga-stuff.

   amiga-stuff is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   amiga-stuff is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with amiga30yrs.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <string.h>

#include <exec/libraries.h>
#include <intuition/intuition.h>

#include <clib/alib_protos.h>
#include <clib/exec_protos.h>
#include <clib/graphics_protos.h>
#include <clib/intuition_protos.h>

#ifdef __VBCC__
#include <clib/alib_stdio_protos.h>
#endif
#include "filereq.h"

#define WIN_LEFT       10
#define WIN_TOP        10
#define WIN_WIDTH      340
#define WIN_HEIGHT     220
#define WIN_TITLE      "IFF Viewer"
#define WIN_MIN_WIDTH  10
#define WIN_MIN_HEIGHT 10
#define WIN_MAX_WIDTH  WIN_WIDTH
#define WIN_MAX_HEIGHT WIN_HEIGHT

#define FILE_MENU_NUM       0
#define NUM_FILE_MENU_ITEMS 2

#define OPEN_MENU_ITEM_NUM  0
#define QUIT_MENU_ITEM_NUM  1

struct NewWindow newwin = {
  WIN_LEFT, WIN_TOP, WIN_WIDTH, WIN_HEIGHT, 0, 1,
  IDCMP_CLOSEWINDOW | IDCMP_MENUPICK | IDCMP_GADGETUP | IDCMP_REQCLEAR,
  WINDOWCLOSE | SMART_REFRESH | ACTIVATE | WINDOWSIZING | WINDOWDRAG | WINDOWDEPTH | NOCAREREFRESH,
  NULL, NULL, WIN_TITLE,
  NULL, NULL,
  WIN_MIN_WIDTH, WIN_MIN_HEIGHT,
  WIN_MAX_WIDTH, WIN_MAX_HEIGHT,
  WBENCHSCREEN
};

struct IntuiText menutext[] = {
  {0, 1, JAM2, 0, 1, NULL, "Open...", NULL},
  {0, 1, JAM2, 0, 1, NULL, "Quit", NULL}
};

struct MenuItem fileMenuItems[] = {
  {&fileMenuItems[1], 0, 0, 0, 0, ITEMTEXT | ITEMENABLED | HIGHCOMP | COMMSEQ, 0,
   &menutext[0], NULL, 'O', NULL, 0},
  {NULL, 0, 0, 0, 0, ITEMTEXT | ITEMENABLED | HIGHCOMP | COMMSEQ, 0,
   &menutext[1], NULL, 'Q', NULL, 0}
};

struct Menu menus[] = {
  {NULL, 20, 0, 0, 0, MENUENABLED | MIDRAWN, "File", &fileMenuItems[0], 0, 0, 0, 0}
};

struct Window *window;

void cleanup()
{
    if (window) {
        ClearMenuStrip(window);
        CloseWindow(window);
    }
}

struct Requester *filereq;

BOOL handle_menu(UWORD menuNum, UWORD itemNum, UWORD subItemNum)
{
    printf("menu, menu num: %d, item num: %d, sub item num: %d\n",
           (int) menuNum, (int) itemNum, (int) subItemNum);
    if (menuNum == FILE_MENU_NUM && itemNum == QUIT_MENU_ITEM_NUM) {
        /* quit */
        return TRUE;
    }
    if (menuNum == FILE_MENU_NUM && itemNum == OPEN_MENU_ITEM_NUM) {
        filereq = open_file(window);
    }
    return FALSE;
}

void handle_events()
{
    BOOL done = FALSE;
    struct IntuiMessage *msg;
    ULONG msgClass;
    UWORD menuCode;
    int buttonId;

    while (!done) {
        Wait(1 << window->UserPort->mp_SigBit);
        if (msg = (struct IntuiMessage *) GetMsg(window->UserPort)) {
            msgClass = msg->Class;
            switch (msgClass) {
            case IDCMP_CLOSEWINDOW:
                done = TRUE;
                break;
            case IDCMP_MENUPICK:
                menuCode = msg->Code;
                done = handle_menu(MENUNUM(menuCode), ITEMNUM(menuCode), SUBNUM(menuCode));
                break;
            case IDCMP_GADGETUP:
                buttonId = (int) ((struct Gadget *) (msg->IAddress))->GadgetID;
                if (buttonId == REQ_OK_BUTTON_ID && filereq) EndRequest(filereq, window);
                else if (buttonId == REQ_CANCEL_BUTTON_ID && filereq) EndRequest(filereq, window);
                break;
            case IDCMP_REQCLEAR:
                puts("requester closed");
                break;
            default:
                break;
            }
            ReplyMsg((struct Message *) msg);
        }
    }
}

void setup_menu()
{
    UWORD txWidth, txHeight, txBaseline, txSpacing, itemWidth, itemHeight, numItems;
    struct RastPort *rp = &window->WScreen->RastPort;
    int i;

    txWidth = rp->TxWidth;
    txHeight = rp->TxHeight;
    txBaseline = rp->TxBaseline;
    txSpacing = rp->TxSpacing;
    printf("TxWidth: %d, TxHeight: %d, TxBaseline: %d, TxSpacing: %d\n",
           (int) txWidth, (int) txHeight, (int) txBaseline, (int) txSpacing);

    /* Set file menu bounds */
    menus[0].Width = TextLength(rp, "File", strlen("File")) + txWidth;
    menus[0].Height = txHeight;

    /* Set file menu items bounds */
    /* We actually need to know what the command uses up */
    itemWidth = txWidth * strlen("Open...") + 50;
    itemHeight = txHeight + 2;  /* 2 pixels adjustment */

    numItems = sizeof(fileMenuItems) / sizeof(struct MenuItem);
    printf("# file items: %d\n", (int) numItems);
    for (i = 0; i < numItems; i++) {
        fileMenuItems[i].TopEdge = i * itemHeight;
        fileMenuItems[i].Height = itemHeight;
        fileMenuItems[i].Width = itemWidth;
    }

    SetMenuStrip(window, &menus[0]);
}

/* Defined automatically in VBCC */
extern struct Library *DOSBase;

int main(int argc, char **argv)
{
    /* version: e.g. 34, revision e.g. 3 for Kickstart 1.3 */
    printf("DOS, version: %d, revision: %d\n",
           (int) DOSBase->lib_Version, (int) DOSBase->lib_Revision);

    /* Adjust the new screen according to the IFF image */
    if (window = OpenWindow(&newwin)) {
        setup_menu();
        // Note: rastport is the entire window, including title bars
        //DrawImage(window->RPort, &image, 2, 10);
        handle_events();
    }
    cleanup();
    return 1;
}