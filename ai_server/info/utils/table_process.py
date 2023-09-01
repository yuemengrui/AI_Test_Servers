# *_*coding:utf-8 *_*
# @Author : YueMengRui


def get_center(box):
    return int(box[0] + (box[2] - box[0]) / 2), int(box[1] + (box[3] - box[1]) / 2)


def split_rows(boxes):
    row_boxes = []
    same_row = []
    c_y = 0
    for box in boxes:
        _, center_y = get_center(box)
        if len(same_row) == 0:
            same_row.append(box)
            c_y = center_y
        else:
            if abs(center_y - c_y) < 6:
                same_row.append(box)
                c_y = center_y
            else:
                row_boxes.append(same_row)
                same_row = []
                same_row.append(box)
                c_y = center_y

    if same_row:
        row_boxes.append(same_row)

    return row_boxes


def split_cols(table):
    cols = []
    center_x_list = []
    for box in table:
        cx, _ = get_center(box)
        if len(center_x_list) == 0:
            center_x_list.append(cx)
            cols.append([box])
        else:
            for i, c_x in enumerate(center_x_list):
                if abs(cx - c_x) < 6:
                    cols[i].append(box)
                    break
            else:
                center_x_list.append(cx)
                cols.append([box])

    return cols

# if __name__ == '__main__':
#     import cv2
#     import random
#
#     img = cv2.imread('/Users/yuemengrui/Downloads/test/images/0.jpg')
#     image, boxes = get_box(img)
#     row_boxes = split_rows(boxes)  # 把所有表格分成一行一行
#
#     # show
#     for row_box in row_boxes:
#         color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#         for box in row_box:
#             cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)
#             cv2.imshow('xx', img)
#             cv2.waitKey(0)
