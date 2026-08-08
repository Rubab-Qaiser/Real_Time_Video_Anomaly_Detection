import { Button } from "@/components/ui/button";

export default function Pagination({
  pagination,
  onPageChange,
}) {
  const { page = 1, pages = 1 } = pagination;

  if (pages <= 1) {
    return null;
  }

  return (
    <div className="mt-5 flex items-center justify-center gap-2">
      <Button
        variant="outline"
        disabled={page === 1}
        onClick={() => onPageChange(page - 1)}
      >
        Previous
      </Button>

      {Array.from({ length: pages }, (_, index) => {
        const pageNumber = index + 1;
        return (
          <Button
            key={pageNumber}
            variant={page === pageNumber ? "default" : "outline"}
            onClick={() => onPageChange(pageNumber)}
          >
            {pageNumber}
          </Button>
        );
      })}

      <Button
        variant="outline"
        disabled={page === pages}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </Button>
    </div>
  );
}