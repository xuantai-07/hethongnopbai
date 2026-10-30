document.addEventListener("DOMContentLoaded", function () {
    // 1. Hiển thị chi tiết đề bài theo bài tập được chọn
    const assignmentSelect = document.getElementById("assignment_id");
    const details = document.querySelectorAll(".assignment-detail");

    if (assignmentSelect) {
        function updateAssignmentDetails() {
            const selectedId = assignmentSelect.value;
            details.forEach(function (detail) {
                detail.hidden = detail.dataset.assignmentId !== selectedId;
            });
        }

        assignmentSelect.addEventListener("change", updateAssignmentDetails);
        updateAssignmentDetails();
    }

    // 2. Kiểm tra định dạng và dung lượng tệp ngay trên trình duyệt (Nhóm 1.3)
    const submitForm = document.getElementById("submit-form");
    const fileInput = document.getElementById("file");

    if (submitForm && fileInput) {
        const allowedExtRaw = submitForm.dataset.allowedExt || "";
        const allowedExts = allowedExtRaw
            .split(",")
            .map(function (s) { return s.trim().toLowerCase(); })
            .filter(Boolean);
        const maxSize = parseInt(submitForm.dataset.maxSize || "0", 10);

        function validateFile() {
            fileInput.setCustomValidity("");
            if (!fileInput.files || fileInput.files.length === 0) {
                return true;
            }
            const file = fileInput.files[0];
            const parts = file.name.split(".");
            const ext = parts.length > 1 ? parts.pop().toLowerCase() : "";

            if (allowedExts.length > 0 && !allowedExts.includes(ext)) {
                const msg =
                    "Định dạng tệp không hợp lệ. Chỉ cho phép: " +
                    allowedExts.map(function (e) { return e.toUpperCase(); }).join(", ") +
                    ".";
                fileInput.setCustomValidity(msg);
                fileInput.reportValidity();
                return false;
            }

            if (file.size === 0) {
                fileInput.setCustomValidity(
                    "Tệp bài làm đang trống (0 byte). Vui lòng chọn tệp hợp lệ."
                );
                fileInput.reportValidity();
                return false;
            }

            if (maxSize > 0 && file.size > maxSize) {
                const maxMb = Math.round(maxSize / (1024 * 1024));
                const msg =
                    "Tệp vượt quá dung lượng tối đa cho phép (" + maxMb + " MB).";
                fileInput.setCustomValidity(msg);
                fileInput.reportValidity();
                return false;
            }

            return true;
        }

        fileInput.addEventListener("change", validateFile);
        submitForm.addEventListener("submit", function (e) {
            if (!validateFile()) {
                e.preventDefault();
            }
        });
    }

    // 3. Hộp thoại xác nhận trước khi đóng/xóa (Nhóm 3.3 & 3.4)
    const confirmForms = document.querySelectorAll("form[data-confirm]");
    confirmForms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const message = form.getAttribute("data-confirm");
            if (message && !window.confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 4. Bật/tắt form sửa bài tập (Nhóm 3.3)
    const editButtons = document.querySelectorAll(".btn-edit-toggle");
    editButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const targetId = btn.getAttribute("data-target");
            const targetEl = targetId ? document.getElementById(targetId) : null;
            if (targetEl) {
                targetEl.hidden = !targetEl.hidden;
            }
        });
    });

    // 5. Tự động lọc khi chọn bài tập ở trang giảng viên (Nhóm 2.3)
    const filterSelect = document.getElementById("filter-assignment");
    if (filterSelect && filterSelect.form) {
        filterSelect.addEventListener("change", function () {
            filterSelect.form.submit();
        });
    }
});
