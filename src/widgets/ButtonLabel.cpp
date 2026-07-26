#include "src/widgets/ButtonLabel.h"

#include <QFileDialog>

ButtonLabel::ButtonLabel(QWidget * parent) : QLabel(parent)
{
    setMinimumSize(10, 0);
}

void ButtonLabel::mouseReleaseEvent(QMouseEvent *)
{
    qInfo("Label clicked");
    emit labelClicked();
}

