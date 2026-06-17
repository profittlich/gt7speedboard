#include "RawRecorder.h"
#include "Helpers.h"

void RawRecorder::start()
{
    DBG_MSG << "Start recording to" << m_filename;
    m_file.setFileName(m_filename);
    m_file.open(QIODeviceBase::WriteOnly);
    if (m_file.isOpen())
    {
        m_recording = true;
    }
    else
    {
        DBG_MSG << "Error opening raw recording:" << m_filename;
    }
}

void RawRecorder::stop()
{
    DBG_MSG << "Stop recording";
    m_recording = false;
    m_file.close();
}

void RawRecorder::setFilename(QString fn)
{
    m_filename = fn;
}

void RawRecorder::newTelemetryPoint(PTelemetryPoint p)
{
    if (m_recording)
    {
        m_file.write(p->getData());
    }
}
