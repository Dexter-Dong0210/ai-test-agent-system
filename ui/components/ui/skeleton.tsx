import { cn } from "@/lib/utils";
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2UmxKWVVRPT06ZmY2N2Y0NmU=

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export { Skeleton };
// TODO  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2UmxKWVVRPT06ZmY2N2Y0NmU=
