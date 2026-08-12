import { mount } from "@vue/test-utils"
import { describe, expect, test } from "vitest"

import Loader from "@/components/Loader.vue"

describe("Loader", () => {
  test("renders the spinner with both bounce elements", () => {
    const wrapper = mount(Loader, {
      props: { size: "40px", backgroundColor: "red" },
    })

    expect(wrapper.find(".spinner").exists()).toBe(true)
    expect(wrapper.find(".double-bounce1").exists()).toBe(true)
    expect(wrapper.find(".double-bounce2").exists()).toBe(true)
  })

  test("applies the size prop to the spinner dimensions", () => {
    const wrapper = mount(Loader, {
      props: { size: "40px", backgroundColor: "red" },
    })

    const style = wrapper.find(".spinner").attributes("style")
    expect(style).toContain("width: 40px")
    expect(style).toContain("height: 40px")
  })

  test("applies the background color prop to the bounce elements", () => {
    const wrapper = mount(Loader, {
      props: { size: "40px", backgroundColor: "rgb(0, 128, 0)" },
    })

    expect(wrapper.find(".double-bounce1").attributes("style")).toContain("background-color: rgb(0, 128, 0)")
    expect(wrapper.find(".double-bounce2").attributes("style")).toContain("background-color: rgb(0, 128, 0)")
  })
})
