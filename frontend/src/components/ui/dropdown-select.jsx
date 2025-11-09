import * as React from "react";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Custom Dropdown Select Component
 * 
 * A dropdown component that avoids ResizeObserver issues by using
 * a simple positioned div instead of Radix UI's Select component.
 */
const DropdownSelectContext = React.createContext({
    open: false,
    setOpen: () => {},
    value: null,
    onValueChange: () => {},
});

export const DropdownSelect = ({
    value,
    onValueChange,
    children,
    className,
    disabled = false,
}) => {
    const [open, setOpen] = React.useState(false);
    const containerRef = React.useRef(null);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        if (disabled && open) {
            setOpen(false);
        }
    }, [disabled, open]);

    React.useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                containerRef.current &&
                !containerRef.current.contains(event.target)
            ) {
                setOpen(false);
            }
        };

        if (open && !disabled) {
            document.addEventListener("mousedown", handleClickOutside);
            // Close on escape key
            const handleEscape = (event) => {
                if (event.key === "Escape") {
                    setOpen(false);
                }
            };
            document.addEventListener("keydown", handleEscape);
            return () => {
                document.removeEventListener("mousedown", handleClickOutside);
                document.removeEventListener("keydown", handleEscape);
            };
        }
    }, [open, disabled]);

    return (
        <DropdownSelectContext.Provider
            value={{
                open: disabled ? false : open,
                setOpen: disabled ? () => {} : setOpen,
                value,
                onValueChange,
            }}
        >
            <div
                ref={containerRef}
                className={cn("relative w-full", className)}
            >
                {children}
            </div>
        </DropdownSelectContext.Provider>
    );
};

export const DropdownSelectTrigger = React.forwardRef(
    ({ className, children, placeholder, disabled, ...props }, ref) => {
        const { open, setOpen, value } = React.useContext(DropdownSelectContext);
        const triggerRef = React.useRef(null);
        React.useImperativeHandle(ref, () => triggerRef.current);

        return (
            <button
                ref={triggerRef}
                type="button"
                onClick={() => !disabled && setOpen(!open)}
                disabled={disabled}
                className={cn(
                    "flex h-12 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
                    open && !disabled && "ring-1 ring-ring",
                    disabled && "bg-gray-50",
                    className
                )}
                {...props}
            >
                <span className={cn("truncate", !value && "text-muted-foreground")}>
                    {children || placeholder || "Select..."}
                </span>
                <ChevronDown
                    className={cn(
                        "h-4 w-4 opacity-50 transition-transform",
                        open && "rotate-180"
                    )}
                />
            </button>
        );
    }
);
DropdownSelectTrigger.displayName = "DropdownSelectTrigger";

export const DropdownSelectContent = React.forwardRef(
    ({ className, children, ...props }, ref) => {
        const { open } = React.useContext(DropdownSelectContext);
        const contentRef = React.useRef(null);

        React.useImperativeHandle(ref, () => contentRef.current);

        if (!open) return null;

        return (
            <div
                ref={contentRef}
                className={cn(
                    "absolute z-50 min-w-[8rem] w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95",
                    className
                )}
                style={{
                    top: "calc(100% + 4px)",
                    left: 0,
                }}
                {...props}
            >
                <div className="p-1 max-h-[300px] overflow-y-auto">
                    {children}
                </div>
            </div>
        );
    }
);
DropdownSelectContent.displayName = "DropdownSelectContent";

export const DropdownSelectItem = React.forwardRef(
    ({ className, children, value, ...props }, ref) => {
        const { value: selectedValue, onValueChange, setOpen } =
            React.useContext(DropdownSelectContext);

        const isSelected = selectedValue === value;

        const handleClick = () => {
            onValueChange(value);
            setOpen(false);
        };

        return (
            <div
                ref={ref}
                role="option"
                aria-selected={isSelected}
                onClick={handleClick}
                className={cn(
                    "relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
                    isSelected && "bg-accent text-accent-foreground",
                    className
                )}
                {...props}
            >
                <span className="absolute right-2 flex h-3.5 w-3.5 items-center justify-center">
                    {isSelected && <Check className="h-4 w-4" />}
                </span>
                <span>{children}</span>
            </div>
        );
    }
);
DropdownSelectItem.displayName = "DropdownSelectItem";

export const DropdownSelectValue = ({ placeholder }) => {
    const { value } = React.useContext(DropdownSelectContext);
    return <span>{value || placeholder || "Select..."}</span>;
};
DropdownSelectValue.displayName = "DropdownSelectValue";

