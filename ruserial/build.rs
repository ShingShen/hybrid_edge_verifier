fn main() {
    cc::Build::new()
    .files([
        "../native/driver.c",
    ])
    .include("native")
    .compile("cdriver");
}
