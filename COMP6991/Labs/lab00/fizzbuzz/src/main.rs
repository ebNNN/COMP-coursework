fn main() {
    for i in 1..=100 {
        // if i % 15 == 0 {
        //     println!("FizzBuzz");
        // } else if i % 3 == 0 {
        //     println!("Fizz");
        // } else if i % 5 == 0 {
        //     println!("Buzz");
        // } else {
        //     println!("{i}");
        // }
        // match block!

        match i {
            i if i % 15 == 0 => println!("FizzBuzz"),
            i if i % 3 == 0 => println!("Fizz"),
            i if i % 5 == 0 => println!("Buzz"),
            _ => println!("{i}"),
        }
    }
}
