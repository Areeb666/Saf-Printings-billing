function printInvoice(invoiceId) {
    let content = document.getElementById("invoice-" + invoiceId).innerHTML;
    let printWindow = window.open("", "", "width=800,height=600");
    printWindow.document.write("<html><head><title>Print Invoice</title></head><body>");
    printWindow.document.write(content);
    printWindow.document.write("</body></html>");
    printWindow.document.close();
    printWindow.print();
}
