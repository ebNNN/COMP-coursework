// 该函数返回的是字符串字面量，也就是编译时已知的固定字符串，
// 它们是存储在只读内存中的常量，无法动态分配和修改。
fn create(b: bool) -> Option<&'static str> {
    if b {
        Some("Hello There")
    } else {
        None
    }
}

fn main() {
    // method 1
    let create_true = create(true);
    if create_true.is_some() {
        println!("create(true) returned {}", create_true.unwrap());
    }

    // method 2
    println!(
        "create(false) returned {}",
        create(false).unwrap_or("<empty>")
    );

    // method 3
    let create_true = create(true);
    match create_true {
        Some(string) => println!("create(true) returned {string}"),
        None         => println!("create(false) returned <empty>"),
    }
}