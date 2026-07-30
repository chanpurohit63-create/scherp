import React from 'react'
import { useParams } from 'react-router-dom'



const ReportCardPrintPreviewPage = () => {
  const { reportCardId } = useParams()
  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Card title="Print Preview" extra={
        <Space>
          <Button icon={<PrinterOutlined />} onClick={() => window.print()}>Print</Button>
          <Button icon={<DownloadOutlined />}>Download PDF</Button>
        </Space>
      }>
        <div style={{ border: '1px solid #d9d9d9', padding: 24, minHeight: 600 }}>
          <Typography.Title level={3} style={{ textAlign: 'center' }}>Report Card Preview</Typography.Title>
          <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
            Student ID: {reportCardId} | Academic Year: 2025-2026
          </Typography.Text>
          <hr style={{ margin: '16px 0' }} />
          <Typography.Text>Subject grades will appear here based on the template configuration.</Typography.Text>
          <hr style={{ margin: '16px 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>Teacher Remark: _________________</div>
            <div>Principal Remark: _________________</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default ReportCardPrintPreviewPage