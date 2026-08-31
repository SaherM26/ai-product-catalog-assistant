import {
  type ChangeEvent,
  useMemo,
  useState,
} from "react";
import "./App.css";

type Product = {
  product_name: string;
  brand: string | null;
  uom: string | null;
  moq: number | null;
  price: number | null;
  hsn: string | null;
  needs_review: boolean;
  review_reason: string | null;
};

type ProcessResponse = {
  success: boolean;
  filename?: string;
  total_products?: number;
  valid_products?: number;
  needs_review?: number;
  products?: Product[];
  error?: string;
};

type Filter = "all" | "valid" | "review";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "/api";

function App() {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [products, setProducts] = useState<Product[]>(
    []
  );

  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [processing, setProcessing] =
    useState(false);

  const [exported, setExported] = useState(false);

  const [activeFilter, setActiveFilter] =
    useState<Filter>("all");

  const filteredProducts = useMemo(() => {
    if (activeFilter === "valid") {
      return products.filter(
        (product) => !product.needs_review
      );
    }

    if (activeFilter === "review") {
      return products.filter(
        (product) => product.needs_review
      );
    }

    return products;
  }, [products, activeFilter]);

  const reviewCount = products.filter(
    (product) => product.needs_review
  ).length;

  const validCount =
    products.length - reviewCount;

  // 0 = nothing yet, 1 = file selected, 2 = processing,
  // 3 = results ready for review, 4 = exported
  const currentStep = exported
    ? 4
    : products.length > 0
      ? 3
      : processing
        ? 2
        : selectedFile
          ? 1
          : 0;

  const stepStatus = (
    step: number
  ): "pending" | "active" | "complete" => {
    if (exported) {
      return "complete";
    }

    if (step < currentStep) {
      return "complete";
    }

    if (step === currentStep) {
      return "active";
    }

    return "pending";
  };

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setProducts([]);
    setStatus("");
    setError("");
    setActiveFilter("all");
    setExported(false);
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setError(
        "Please select a supplier file first."
      );
      return;
    }

    setProcessing(true);
    setError("");
    setStatus(
      "Reading file and extracting product data..."
    );
    setProducts([]);
    setActiveFilter("all");
    setExported(false);

    try {
      const formData = new FormData();

      formData.append(
        "file",
        selectedFile
      );

      const response = await fetch(
        `${API_URL}/process`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data: ProcessResponse =
        await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
          "The file could not be processed."
        );
      }

      const resultProducts =
        data.products ?? [];

      setProducts(resultProducts);

      setStatus(
        `Completed successfully — ${data.total_products ?? 0
        } products processed.`
      );
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Something went wrong while processing the file.";

      setError(message);
      setStatus("");
    } finally {
      setProcessing(false);
    }
  };

  const handleExport = async () => {
    if (!products.length) {
      setError(
        "There are no processed products to export."
      );
      return;
    }

    try {
      setError("");

      const response = await fetch(
        `${API_URL}/export`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            products,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Could not generate the Excel file."
        );
      }

      const blob =
        await response.blob();

      const url =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;
      link.download =
        "validated_products.xlsx";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);

      setExported(true);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Export failed.";

      setError(message);
    }
  };

  const reset = () => {
    setSelectedFile(null);
    setProducts([]);
    setStatus("");
    setError("");
    setActiveFilter("all");
    setExported(false);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            PC
          </div>

          <div>
            <div className="brand-name">
              Product Catalog Assistant
            </div>

            <div className="brand-caption">
              Supplier data processing
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          System ready
        </div>
      </header>

      <main className="page">
        <section
          className={
            products.length > 0
              ? "hero hero-compact"
              : "hero"
          }
        >
          <div className="hero-copy">
            <div className="eyebrow">
              AI-POWERED OPERATIONS
            </div>

            <h1>
              Turn supplier files into
              <span>
                validated product data.
              </span>
            </h1>

            <p>
              Extract, normalize, validate,
              review, and export supplier
              product information from one
              simple workflow.
            </p>
          </div>

          <div className="workflow-strip">
            <div
              className={`workflow-step ${stepStatus(1)}`}
            >
              <span>01</span>
              Extract
            </div>

            <div
              className={`workflow-line ${stepStatus(1) === "complete" ? "filled" : ""
                }`}
            />

            <div
              className={`workflow-step ${stepStatus(2)}`}
            >
              <span>02</span>
              Validate
            </div>

            <div
              className={`workflow-line ${stepStatus(2) === "complete" ? "filled" : ""
                }`}
            />

            <div
              className={`workflow-step ${stepStatus(3)}`}
            >
              <span>03</span>
              Review
            </div>

            <div
              className={`workflow-line ${stepStatus(3) === "complete" ? "filled" : ""
                }`}
            />

            <div
              className={`workflow-step ${stepStatus(4)}`}
            >
              <span>04</span>
              Export
            </div>
          </div>
        </section>

        <section className="upload-card">
          <div className="card-heading">
            <div>
              <h2>
                Upload supplier file
              </h2>

              <p>
                Supported formats: PDF, XLSX,
                XLS
              </p>
            </div>

            {selectedFile && (
              <button
                className="text-button"
                onClick={reset}
                type="button"
              >
                Clear
              </button>
            )}
          </div>

          <label
            className={
              selectedFile
                ? "drop-zone has-file"
                : "drop-zone"
            }
          >
            <input
              type="file"
              accept=".pdf,.xlsx,.xls"
              onChange={handleFileChange}
            />

            <div className="upload-icon">
              {selectedFile ? "✓" : "↑"}
            </div>

            {selectedFile ? (
              <>
                <strong>
                  {selectedFile.name}
                </strong>

                <span>
                  File selected · Ready to process
                </span>
              </>
            ) : (
              <>
                <strong>
                  Drop your file here
                </strong>

                <span>
                  or click to browse from
                  your computer
                </span>
              </>
            )}
          </label>

          {selectedFile && (
            <div className="file-meta">
              <div className="file-meta-item">
                <span>FILE</span>
                <strong>
                  {selectedFile.name}
                </strong>
              </div>

              <div className="file-meta-item">
                <span>TYPE</span>
                <strong>
                  {selectedFile.name
                    .split(".")
                    .pop()
                    ?.toUpperCase()}
                </strong>
              </div>

              <div className="file-meta-item">
                <span>SIZE</span>
                <strong>
                  {(
                    selectedFile.size /
                    1024
                  ).toFixed(1)}{" "}
                  KB
                </strong>
              </div>
            </div>
          )}

          <div className="upload-actions">
            <button
              className="primary-button"
              onClick={handleProcess}
              disabled={
                !selectedFile ||
                processing
              }
              type="button"
            >
              {processing
                ? "Processing..."
                : "Process supplier file"}
            </button>

            <div className="privacy-note">
              Files are processed for the
              current workflow.
            </div>
          </div>

          {processing && (
            <div className="processing-panel">
              <div className="processing-spinner" />

              <div>
                <strong>
                  Processing supplier data
                </strong>

                <span>
                  Extracting and validating
                  product records with AI...
                </span>
              </div>
            </div>
          )}

          {!processing && status && (
            <div className="success-message">
              <span>✓</span>
              {status}
            </div>
          )}

          {error && (
            <div className="error-message">
              <span>!</span>
              {error}
            </div>
          )}
        </section>

        {products.length > 0 && (
          <section className="results-card">
            <div className="results-heading">
              <div>
                <div className="eyebrow">
                  PROCESSING RESULT
                </div>

                <h2>
                  Validation summary
                </h2>

                <p>
                  Review flagged records
                  before exporting the
                  final dataset.
                </p>
              </div>

              <div className="results-actions">
                <button
                  className="secondary-button"
                  onClick={reset}
                  type="button"
                >
                  Process another
                </button>

                <button
                  className="download-button"
                  onClick={handleExport}
                  type="button"
                >
                  Download Excel
                </button>
              </div>
            </div>

            <div className="file-result-bar">
              <div>
                <span>
                  SOURCE FILE
                </span>

                <strong>
                  {selectedFile?.name}
                </strong>
              </div>

              <div>
                <span>
                  WORKFLOW
                </span>

                <strong>
                  Extracted → Validated
                </strong>
              </div>
            </div>

            <div className="metrics">
              <div className="metric">
                <span>
                  Total products
                </span>

                <strong>
                  {products.length}
                </strong>
              </div>

              <div className="metric">
                <span>
                  Ready to use
                </span>

                <strong className="success-number">
                  {validCount}
                </strong>
              </div>

              <div className="metric review">
                <span>
                  Needs review
                </span>

                <strong>
                  {reviewCount}
                </strong>
              </div>
            </div>

            {reviewCount > 0 && (
              <div className="review-banner">
                <div className="review-symbol">
                  !
                </div>

                <div>
                  <strong>
                    {reviewCount} record
                    {reviewCount !== 1
                      ? "s"
                      : ""}{" "}
                    need human review
                  </strong>

                  <span>
                    Missing or ambiguous
                    information has been
                    flagged instead of
                    being guessed.
                  </span>
                </div>
              </div>
            )}

            <div className="table-toolbar">
              <div className="filters">
                <button
                  className={
                    activeFilter === "all"
                      ? "filter active"
                      : "filter"
                  }
                  onClick={() =>
                    setActiveFilter("all")
                  }
                  type="button"
                >
                  All
                  <span>
                    {products.length}
                  </span>
                </button>

                <button
                  className={
                    activeFilter === "valid"
                      ? "filter active"
                      : "filter"
                  }
                  onClick={() =>
                    setActiveFilter("valid")
                  }
                  type="button"
                >
                  Valid
                  <span>
                    {validCount}
                  </span>
                </button>

                <button
                  className={
                    activeFilter === "review"
                      ? "filter active review-filter"
                      : "filter review-filter"
                  }
                  onClick={() =>
                    setActiveFilter("review")
                  }
                  type="button"
                >
                  Needs review
                  <span>
                    {reviewCount}
                  </span>
                </button>
              </div>

              <div className="table-count">
                Showing{" "}
                <strong>
                  {filteredProducts.length}
                </strong>{" "}
                records
              </div>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>
                      Product
                    </th>

                    <th>
                      Brand
                    </th>

                    <th>
                      UOM
                    </th>

                    <th>
                      MOQ
                    </th>

                    <th>
                      Price
                    </th>

                    <th>
                      HSN
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Review reason
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {filteredProducts.map(
                    (product, index) => (
                      <tr
                        key={`${product.product_name}-${index}`}
                        className={
                          product.needs_review
                            ? "review-row"
                            : ""
                        }
                      >
                        <td className="product-cell">
                          {product.product_name}
                        </td>

                        <td>
                          {product.brand ??
                            "—"}
                        </td>

                        <td>
                          {product.uom ??
                            "—"}
                        </td>

                        <td>
                          {product.moq ??
                            "—"}
                        </td>

                        <td>
                          {product.price ??
                            "—"}
                        </td>

                        <td>
                          {product.hsn ??
                            "—"}
                        </td>

                        <td>
                          {product.needs_review ? (
                            <span className="status-pill review-pill">
                              Needs review
                            </span>
                          ) : (
                            <span className="status-pill valid-pill">
                              Valid
                            </span>
                          )}
                        </td>

                        <td className="reason-cell">
                          {product.review_reason ??
                            "No action required"}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>

              {filteredProducts.length ===
                0 && (
                  <div className="empty-filter">
                    No records match this filter.
                  </div>
                )}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>
          AI Product Catalog & Price List
          Assistant
        </span>

        <span>
          •
        </span>

        <span>
          Structured extraction · Validation ·
          Human review
        </span>
      </footer>
    </div>
  );
}

export default App;